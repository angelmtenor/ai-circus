# AGENTS.md - GenAI Development & Verification Guide

This document defines the strict operational standards for GenAI assistants (including Gemini CLI and project-internal agents) when developing, refactoring, or verifying this repository.

## 1. Development Principles

### Single Source of Truth for Config
- **Mandate:** All application settings MUST be defined in `env_config.yaml`.
- **Workflow:** When adding a new environment variable:
    1. Update `env_config.yaml`.
    2. Run `make generate` to synchronize `src/ai_circus/data_model.py` and `.env.example`.
- **Prohibition:** NEVER define redundant `Settings` classes or load `.env` files manually using `dotenv` or `os.getenv` for core app logic. Always use `ai_circus.get_env_config()`.

### Simplified Public API
- **Mandate:** Prefer importing core functions directly from the package root:
    ```python
    from ai_circus import get_llm, get_embeddings, get_env_config
    ```
- **Prohibition:** Avoid deep internal imports (e.g., `ai_circus.models.get_llm`) unless specifically required for low-level overrides.

### Model & Parameter Standards
- **Standard Models:** Default to `gemini-3-flash-preview` (Google) or `gpt-5.4-mini` (OpenAI).
- **LangChain Usage:** Use standard LangChain parameters (`model`, `api_key`, `temperature`, `base_url`).
- **Prohibition:** DO NOT pass non-standard parameters like `verbosity` or `reasoning_effort` to the `ChatOpenAI` constructor unless they are officially supported in the version used.

## 2. Git & Security Hygiene

- **Sensitive Files:** Files starting with `.env*` (except `.env.example`) and the `backups/` directory MUST remain ignored in `.gitignore`.
- **Backups:** When performing a `make clean`, ensure existing `.env` files are backed up to the `backups/` folder with a timestamp.

## 3. The Verification Pipeline

An agent's task is NOT complete until it has passed the full verification pipeline.

### Step 1: Quality Assurance & Unit Testing
- Run `make check` to execute `qa` (linting/formatting) and `test` (unit tests).
- If `make generate` was run, ensure the resulting code is formatted (the `Makefile` target handles this automatically).

### Step 2: End-to-End Verification
- **Mandate:** Before proposing a commit or final solution, run `make all`.
- **Pipeline:** `clean` -> `setup` -> `check` -> `run`.
- This ensures that the environment can be built from scratch, quality checks pass, and the application smoke test (`make run`) succeeds.

### Step 3: Test Coverage
- ALWAYS update or create test cases in the `tests/` directory for any logic changes.
- Use mocks (via `monkeypatch`) for LLM calls to keep tests fast and deterministic.

## 4. Documentation Responsibility
- Keep docstrings updated with accurate `Author` and `Date` (standardize on 2026).
- Update `README.md` if the user-facing onboarding or CLI toolset changes.
- Ensure `src/ai_circus/__init__.py` properly exports new public components via `__all__`.
