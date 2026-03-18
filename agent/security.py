"""Saf3AI security callbacks for the Nykaa ADK agent.

Scans prompts and responses for threats. Behaviour is controlled via env vars:
  SECURITY_SCAN_ENABLED  - set to "true" to enable (default: disabled)
  THREAT_ACTION_LEVEL    - BLOCK | WARN | LOG | OFF  (default: BLOCK)
  SECURITY_API_ENDPOINT  - scanner endpoint (default: https://scanner-dev.saf3ai.com)
  SECURITY_API_KEY       - API key for the scanner
  SECURITY_API_TIMEOUT   - request timeout in seconds (default: 30)
"""

import logging
import os
from typing import Any, Dict, Optional, Tuple

try:
    from saf3ai_sdk import create_security_callback

    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    create_security_callback = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


def security_policy(
    text: str,
    scan_results: Dict[str, Any],
    text_type: str = "prompt",
) -> bool:
    """Saf3AI security policy applied after every scan.

    Returns True  → allow the text through.
    Returns False → block the text (only meaningful when THREAT_ACTION_LEVEL=BLOCK).
    """
    action_level = os.getenv("THREAT_ACTION_LEVEL", "BLOCK").upper()
    detection_results = scan_results.get("detection_results", {})

    threats_found = [
        threat_type
        for threat_type, result_data in detection_results.items()
        if result_data.get("result") == "MATCH_FOUND"
    ]

    if action_level == "OFF":
        return True

    if threats_found:
        threat_list = ", ".join(threats_found)

        if action_level == "BLOCK":
            logger.warning("BLOCKING %s: %s", text_type.upper(), threat_list)
            return False

        if action_level == "WARN":
            logger.warning("WARNING %s: %s", text_type.upper(), threat_list)
            return True

        if action_level == "LOG":
            logger.info("LOG %s: %s", text_type.upper(), threat_list)
            return True

    logger.info(
        "Security scan (%s): %d threats found, action=%s",
        text_type,
        len(threats_found),
        action_level,
    )
    return True


def build_security_callbacks(
    agent_identifier: str,
) -> Tuple[Optional[Any], Optional[Any]]:
    """Create Saf3AI before/after model callbacks for an ADK LlmAgent.

    Returns:
        (before_model_callback, after_model_callback).
        Both are None when security is unavailable or disabled.
    """
    if not SECURITY_AVAILABLE:
        logger.warning("Saf3AI SDK not installed — security scanning disabled.")
        return None, None

    if os.getenv("SECURITY_SCAN_ENABLED", "false").lower() != "true":
        logger.info("Security scanning disabled (SECURITY_SCAN_ENABLED != true).")
        return None, None

    try:
        api_endpoint = os.getenv(
            "SECURITY_API_ENDPOINT",
            "https://scanner-dev.saf3ai.com",
        )
        api_key = os.getenv("SECURITY_API_KEY")
        timeout = int(os.getenv("SECURITY_API_TIMEOUT", "30"))

        before_cb, after_cb = create_security_callback(
            api_endpoint=api_endpoint,
            api_key=api_key,
            timeout=timeout,
            on_scan_complete=security_policy,
            scan_responses=True,
            agent_identifier=agent_identifier,
        )

        # The SDK defines its inner callbacks with keyword-only parameters
        # (def security_callback(*, callback_context, llm_request, ...)) but ADK
        # invokes before_model_callback / after_model_callback positionally.
        # These thin wrappers bridge that mismatch.
        def before_model_wrapper(callback_context: Any, llm_request: Any) -> Any:
            return before_cb(
                callback_context=callback_context, llm_request=llm_request
            )

        def after_model_wrapper(callback_context: Any, llm_response: Any) -> Any:
            return after_cb(
                callback_context=callback_context, llm_response=llm_response
            )

        logger.info("Security callbacks created for agent: %s", agent_identifier)
        return before_model_wrapper, after_model_wrapper

    except Exception as exc:
        logger.error(
            "Failed to initialise security callbacks: %s",
            exc,
            exc_info=True,
        )
        return None, None

