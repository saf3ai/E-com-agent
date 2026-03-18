from typing import Any

from google.adk import Agent

from .config import MODEL_NAME as LEGACY_MODEL_NAME
from .saf3ai_setup import traceable
from .settings import settings
from .security import build_security_callbacks
from tools.product_search import search_products
from tools.order_management import create_order, track_order, cancel_order
from tools.recommendations import recommend_products


def _load_system_prompt() -> str:
    import os

    base_dir = os.path.dirname(os.path.dirname(__file__))
    prompt_path = os.path.join(base_dir, "prompts", "system_prompt.txt")
    try:
        with open(prompt_path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "You are Ecommerce Assistant, a premium beauty and fashion shopping assistant. "
            "Help users with product discovery, recommendations, and order support."
        )


settings.validate_for_startup()

GLOBAL_INSTRUCTION = _load_system_prompt()
INSTRUCTION = GLOBAL_INSTRUCTION


_security_before, _security_after = build_security_callbacks(
    agent_identifier="ecommerce_agent"
)

ecommerce_agent = Agent(
    model=settings.MODEL_NAME or LEGACY_MODEL_NAME,
    global_instruction=GLOBAL_INSTRUCTION,
    instruction=INSTRUCTION,
    name="ecommerce_agent",
    tools=[
        search_products,
        create_order,
        track_order,
        cancel_order,
        recommend_products,
    ],
    before_model_callback=_security_before,
    after_model_callback=_security_after,
)


def run_agent(query: str) -> Any:
    """Run the ecommerce agent for a single user query."""
    response = ecommerce_agent.run(query)
    return response


# Expose a root_agent symbol so ADK Web can discover this agent.
root_agent = ecommerce_agent

