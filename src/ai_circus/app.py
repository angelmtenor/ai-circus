"""
app.py
------

Entry point for the AI Circus application.
Initializes configuration, logs environment state, and performs
a simple LLM test call.

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

from ai_circus.core.logger import logger
from ai_circus.data_model import EnvConfig, env_config
from ai_circus.models import get_llm


def initialize_and_log_settings() -> None:
    """Load settings and log them with redacted secrets."""
    logger.info("--- Initializing Application Settings ---")
    for field in EnvConfig.model_fields:
        val = getattr(env_config, field)
        # Redaction logic consistent with setup scripts
        if hasattr(val, "get_secret_value"):
            secret_val = val.get_secret_value()
            val = "****" + secret_val[-4:] if secret_val else "None"
        logger.info("{}: {}", field, val)


def run_hello_world() -> None:
    """Perform a simple hello world call to the LLM."""
    language = env_config.LLM_LANGUAGE or "English"
    logger.info("Starting Hello World LLM call in {}", language)

    try:
        llm = get_llm(provider="openai")
        prompt = f"Say 'Hello world' and a very brief welcome message in {language}."
        response = llm.invoke(prompt)
        logger.success("LLM Response: {}", response.content)
    except Exception:
        logger.exception("Failed to connect to the LLM. Check your API keys and connection.")


def main() -> None:
    """Main application entry point."""
    initialize_and_log_settings()
    run_hello_world()


if __name__ == "__main__":
    main()
