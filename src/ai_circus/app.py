"""
app.py
------

Entry point for the AI Circus application.
Initializes configuration, logs environment state, and performs
a simple LLM test call.

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

import sys

from pydantic import ValidationError

from ai_circus import get_env_config, get_llm
from ai_circus.core.logger import configure_logger, get_logger

logger = get_logger(__name__)


def main() -> None:
    """Main application entry point."""
    configure_logger()

    try:
        config = get_env_config()
    except ValidationError as e:
        logger.error("Configuration error: Mandatory environment variable(s) missing or invalid:")
        for error in e.errors():
            logger.error("  {}: {}", " -> ".join(str(loc) for loc in error["loc"]), error["msg"])
        sys.exit(1)

    import os

    current_env = os.getenv("APP_ENV", "local")
    logger.info("--- Initializing Application Settings (ENV: {}) ---", current_env)
    # Redaction logic consistent with setup scripts
    for field_name in config.model_fields:
        val = getattr(config, field_name)
        if hasattr(val, "get_secret_value"):
            secret_val = val.get_secret_value()
            val = "****" + secret_val[-4:] if secret_val else "None"
        logger.info("{}: {}", field_name, val)

    language = config.LLM_LANGUAGES
    logger.info("Starting Hello World LLM call in {}", language)

    try:
        llm = get_llm()
        prompt = f"Say 'Hello world' and a very brief welcome message in {language}."
        response = llm.invoke(prompt)
        logger.success("LLM Response: {}", response.content)
    except Exception:
        logger.exception("Failed to connect to the LLM. Check your API keys and connection.")


if __name__ == "__main__":
    main()
