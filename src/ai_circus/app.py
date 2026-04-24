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

from ai_circus.core.logger import configure_logger, get_logger

logger = get_logger(__name__)


def main() -> None:
    """Main application entry point."""
    configure_logger()

    try:
        from ai_circus.data_model import EnvConfig, get_env_config

        env_config = get_env_config()
    except ValidationError as e:
        logger.error("Configuration error: Mandatory environment variable(s) missing or invalid:")
        for error in e.errors():
            logger.error("  {}: {}", " -> ".join(str(loc) for loc in error["loc"]), error["msg"])
        sys.exit(1)

    # If validation passes, continue with initialization and app logic
    from ai_circus.models import get_llm

    logger.info("--- Initializing Application Settings ---")
    for field in EnvConfig.model_fields:
        val = getattr(env_config, field)
        # Redaction logic consistent with setup scripts
        if hasattr(val, "get_secret_value"):
            secret_val = val.get_secret_value()
            val = "****" + secret_val[-4:] if secret_val else "None"
        logger.info("{}: {}", field, val)

    language = env_config.LLM_LANGUAGES or "English"
    logger.info("Starting Hello World LLM call in {}", language)

    try:
        llm = get_llm(provider="openai")
        prompt = f"Say 'Hello world' and a very brief welcome message in {language}."
        response = llm.invoke(prompt)
        logger.success("LLM Response: {}", response.content)
    except Exception:
        logger.exception("Failed to connect to the LLM. Check your API keys and connection.")


if __name__ == "__main__":
    main()
