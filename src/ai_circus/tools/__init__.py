"""Tools module for AI Circus.

This module provides command-line tools and utilities:
- check_api_keys: Verify API key configurations
- generate_commits_messages: Generate commit messages using LLMs
- generate_data_model: Regenerate data_model.py/.env.example from settings.yaml
- hello_world: Basic demonstration tool
"""

from __future__ import annotations

from .check_api_keys import main as check_api_keys
from .generate_commits_messages import run_main as generate_commits_messages
from .generate_data_model import check_env_drift
from .generate_data_model import main as generate_data_model
from .hello_world import main as hello_world

__all__ = [
    "check_api_keys",
    "check_env_drift",
    "generate_commits_messages",
    "generate_data_model",
    "hello_world",
]
