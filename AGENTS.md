# AGENTS.md - GenAI Development & Verification Guide

This document defines the foundational mandates and operational workflows for GenAI assistants (including Gemini CLI and project-internal agents). Adherence to these rules is mandatory to ensure repository integrity, security, and quality.

## 1. Core Mandates (Priority Zero)

### 🚨 Security & System Integrity
- **Credential Protection:** NEVER log, print, or commit secrets, API keys, or sensitive credentials.
- **Ignore Rules:** Files matching `.env*` (except `.env.example`) and the `backups/` directory MUST remain ignored in `.gitignore`.
- **Pre-Commit Audit:** Before proposing a commit, agents must verify that no sensitive data or temporary `.env` files are in the staged changes.

### 👥 Human-in-the-Loop Protocol
- **Inspection Required:** Agents must never commit code until the human operator has inspected the proposed changes and provided explicit validation.
- **No Pushing:** Agents are STRICTLY PROHIBITED from running `git push`. All updates to remote repositories must be performed manually by the user.
- **Confirmation Loop:** For every destructive or significant operation, explain the intent first and wait for approval.

### ✅ Verification is Mandatory
- **Definition of Done:** A task is NOT complete until `make check` (QA + Test) and `make run` (App Smoke Test) pass successfully.
- **End-to-End Pipeline:** For significant refactors or initial setups, run `make all` to verify the entire lifecycle: `clean` -> `setup` -> `check` -> `run`.
- **Test-Driven:** Every bug fix or feature implementation must include corresponding unit tests in the `tests/` directory. Use mocks (via `monkeypatch`) to ensure tests are fast and deterministic.

## 2. Development Standards

### Single Source of Truth for Configuration
- **Centralized Config:** All application settings MUST be defined in `env_config.yaml`.
- **Synchronization:** When changing settings:
    1. Update `env_config.yaml`.
    2. Run `make generate` to sync `src/ai_circus/data_model.py` and `.env.example`.
- **Prohibition:** NEVER define redundant `Settings` classes or load `.env` files manually using `dotenv` for core app logic. Always use `ai_circus.get_env_config()`.

### Simplified Public API & Architecture
- **Package Root Imports:** Prefer importing core functions directly from the package root:
    ```python
    from ai_circus import get_llm, get_embeddings, get_env_config
    ```
- **Standard Models:** Default to `gemini-3-flash-preview` (Google) and `gpt-5.4-mini` (OpenAI).
- **LangChain Usage:** Use standard parameters (`model`, `api_key`, `temperature`). Avoid non-standard args like `verbosity` or `reasoning_effort` in constructors.

### Scripting & Portability
- **Makefile Constraints:** Target bodies in the `Makefile` must be kept short to satisfy the `checkmake` linter. Delegate complex logic to dedicated Python scripts.
- **Safe Redirection:** Never use `sed -i` (non-portable). Use the safe pattern: `sed '...' file > file.tmp && mv file.tmp file`.

## 3. Git Workflow & Hygiene

- **Branching Conventions:** Use descriptive branch names grouped by intent (e.g., `feature/...`, `fix/...`, `docs/...`).
- **Commit Standards:** Adhere to the Conventional Commits format to maintain a clear history.
- **Preservation:** The `make clean` target must preserve dated `.env` backups in the `backups/` folder.

## 4. Documentation Responsibility

- **Docstring Accuracy:** Keep docstrings updated with standard headers: `Author: Angel Martinez-Tenor, 2026`.
- **Module Exports:** Ensure `src/ai_circus/__init__.py` properly exports all new public components via `__all__`.
- **README Updates:** Update the "Quick Start" or "CLI Tools" sections if the onboarding workflow or available scripts change.
