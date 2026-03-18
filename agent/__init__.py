"""Expose Nykaa root_agent for ADK Web discovery."""

from .main_agent import root_agent
from . import main_agent as agent

__all__ = ["root_agent", "agent"]

