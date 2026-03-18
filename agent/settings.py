from __future__ import annotations

import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime configuration for the ecommerce agent.

    In Cloud Run, set environment variables directly (recommended).
    For local ADK Web, a `.env` file under `agent/` can be used.
    """

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM backend (Gemini API by default)
    GOOGLE_API_KEY: str | None = Field(default=None)
    GOOGLE_GENAI_USE_VERTEXAI: str = Field(default="0")

    # Vertex AI (only required when GOOGLE_GENAI_USE_VERTEXAI=1)
    GOOGLE_CLOUD_PROJECT: str | None = Field(default=None)
    GOOGLE_CLOUD_LOCATION: str = Field(default="us-central1")

    # Agent behavior
    MODEL_NAME: str = Field(default="gemini-2.5-pro")
    MAX_RESULTS: int = Field(default=15, ge=1, le=50)

    # Observability / logging
    LOG_LEVEL: str = Field(default="INFO")

    # Security scanning toggles (Saf3AI)
    SECURITY_SCAN_ENABLED: str = Field(default="false")
    THREAT_ACTION_LEVEL: str = Field(default="BLOCK")

    def validate_for_startup(self) -> None:
        """Fail fast on invalid/unsafe configuration."""
        using_vertex = self.GOOGLE_GENAI_USE_VERTEXAI.lower() in {"1", "true", "yes"}
        if using_vertex:
            if not self.GOOGLE_CLOUD_PROJECT:
                raise ValueError("GOOGLE_CLOUD_PROJECT is required when using Vertex AI.")
            if not self.GOOGLE_CLOUD_LOCATION:
                raise ValueError(
                    "GOOGLE_CLOUD_LOCATION is required when using Vertex AI."
                )
        else:
            if not self.GOOGLE_API_KEY:
                raise ValueError(
                    "GOOGLE_API_KEY is required when using the Gemini API backend."
                )


settings = Settings()

