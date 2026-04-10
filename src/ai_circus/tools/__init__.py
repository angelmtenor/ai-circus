"""Tools module for AI Circus.

This module provides command-line tools and utilities:
- check_api_keys: Verify API key configurations
- generate_commits_messages: Generate commit messages using LLMs
- hello_world: Basic demonstration tool
"""

from __future__ import annotations

from .check_api_keys import main as check_api_keys
from .generate_commits_messages import run_main as generate_commits_messages
from .hello_world import main as hello_world

__all__ = [
    "check_api_keys",
    "generate_commits_messages",
    "hello_world",
]
