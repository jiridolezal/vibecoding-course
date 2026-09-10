"""Runtime configuration, read from the environment (optionally via a .env file)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Connection details for an OpenAI-compatible chat completions endpoint."""

    base_url: str
    api_key: str
    model: str
    max_tool_rounds: int

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            base_url=os.getenv("LLM_BASE_URL", "http://localhost:1234/v1"),
            api_key=os.getenv("LLM_API_KEY", "lm-studio"),
            model=os.getenv("LLM_MODEL", "google/gemma-4-e4b"),
            max_tool_rounds=int(os.getenv("LLM_MAX_TOOL_ROUNDS", "5")),
        )
