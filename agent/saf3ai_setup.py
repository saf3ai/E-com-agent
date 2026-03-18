"""
Saf3AI SDK setup for the Nykaa demo agent (saf3ai-sdk==0.2.35).

Must be imported before agent/tools init runs so traces appear in Saf3AI UI.
"""

import logging
import os

# Suppress noisy OpenTelemetry TracerProvider messages
logging.getLogger("opentelemetry.sdk.trace").setLevel(logging.ERROR)
logging.getLogger("opentelemetry.trace").setLevel(logging.ERROR)
logging.getLogger("saf3ai_sdk").setLevel(logging.WARNING)

# No-op fallback when Saf3AI is not configured
traceable = lambda f: f  # noqa: E731


def _init_saf3ai() -> None:
    """Initialize Saf3AI SDK if the required env vars are present."""
    global traceable

    saf3ai_api_key = os.getenv("SAF3AI_API_KEY", "")
    saf3ai_collector_agent = os.getenv("SAF3AI_COLLECTOR_AGENT", "")
    saf3ai_scanner_endpoint = os.getenv("SAF3AI_SCANNER_ENDPOINT", "")
    saf3ai_scanner_api_key = os.getenv("SAF3AI_SCANNER_API_KEY", "")

    if not saf3ai_api_key or not saf3ai_collector_agent:
        return

    try:
        from saf3ai_sdk import init as saf3ai_init  # type: ignore[import]
        from saf3ai_sdk import traceable as saf3ai_traceable  # type: ignore[import]

        init_params: dict = {
            "agent_id": os.getenv("SAF3AI_AGENT_ID", "nykaa-bot-agent"),
            "api_key": saf3ai_api_key,
            "safeai_collector_agent": saf3ai_collector_agent,
            "framework": "google-adk",
        }

        if os.getenv("SAF3AI_SERVICE_NAME"):
            init_params["service_name"] = os.getenv("SAF3AI_SERVICE_NAME")
        if os.getenv("SAF3AI_ENVIRONMENT"):
            init_params["environment"] = os.getenv("SAF3AI_ENVIRONMENT")
        if os.getenv("SAF3AI_LOG_LEVEL"):
            init_params["log_level"] = os.getenv("SAF3AI_LOG_LEVEL")
        if os.getenv("SAF3AI_DEBUG_MODE", "false").lower() == "true":
            init_params["debug_mode"] = True
        if os.getenv("SAF3AI_CONSOLE_OUTPUT", "false").lower() == "true":
            init_params["console_output"] = True
        if saf3ai_scanner_endpoint:
            init_params["scanner_endpoint"] = saf3ai_scanner_endpoint
        if saf3ai_scanner_api_key:
            init_params["scanner_api_key"] = saf3ai_scanner_api_key

        saf3ai_init(**init_params)
        traceable = saf3ai_traceable
        print("Saf3AI: SDK initialized - traces will appear in Saf3AI UI")
    except Exception as e:  # noqa: BLE001
        print(f"Saf3AI: Init failed - {e}")
        print("Nykaa agent will run without Saf3AI tracing.")


# Run on import — must happen before agent/tools are loaded
_init_saf3ai()

