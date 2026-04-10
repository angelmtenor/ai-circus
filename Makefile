# Author: Angel Martinez-Tenor, 2025. Adapted from https://github.com/angelmtenor/ds-template

VENV_DIR      := .venv
.DEFAULT_GOAL := help

CYAN  := $(shell tput setaf 6 2>/dev/null)
RESET := $(shell tput sgr0 2>/dev/null)

.PHONY: help setup install check update qa test unused-packages all build clean zip spacy-models generate ai-hello-world ai-check-api-keys ai-commit ai-sample-assistant ai-sample-agentic ai-generate-data-model

# ── Help ──────────────────────────────────────────────────────────────────────

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS=":.*?## "}; {printf "  $(CYAN)%-22s$(RESET) %s\n", $$1, $$2}'

# ── Bootstrap ─────────────────────────────────────────────────────────────────

setup: ## Complete setup: install dependencies, download models, and verify environment (run after cloning)
	@echo "🚀 Starting complete setup..."
	@uv sync --extra optional && uv run pre-commit install && uv run python -m spacy download en_core_web_sm || { echo "❌ setup failed or spaCy download failed (may require manual: make spacy-models)"; exit 1; }
	@$(MAKE) generate
	@uv run python check_full_env.py || { echo "❌ Environment check failed."; exit 1; }
	@echo "✓ Complete setup finished!"

install: ## Sync deps, install pre-commit hooks, and download spaCy models (run after cloning)
	@uv sync --extra optional     || { echo "❌ uv sync failed."; exit 1; }
	@uv run pre-commit install    || { echo "❌ pre-commit install failed."; exit 1; }
	@uv run python -m spacy download en_core_web_sm || { echo "⚠️  spaCy model download failed (may require manual: make spacy-models)"; }
	@echo "✓ install complete"

check: ## Verify full environment (venv, uv, packages, env vars)
	@uv run python check_full_env.py || { echo "❌ Environment check failed."; exit 1; }
	@echo "✓ Environment ready"

update: ## Upgrade lockfile, sync deps & update pre-commit hooks
	@uv lock --upgrade            || { echo "❌ uv lock upgrade failed."; exit 1; }
	@uv sync --extra optional     || { echo "❌ uv sync failed."; exit 1; }
	@uv run pre-commit autoupdate || { echo "❌ pre-commit autoupdate failed."; exit 1; }
	@$(MAKE) generate
	@echo "✓ update complete"

# ── Dev workflow ──────────────────────────────────────────────────────────────

generate: ## Generate Pydantic data model from env_config.yaml
	@uv run ai-generate-data-model

qa: ## Run all pre-commit checks (ruff, ruff-format, etc.)
	@uv run pre-commit run --all-files || { echo "❌ qa failed."; exit 1; }
	@echo "✓ qa complete"

test: ## Run test suite
	@uv run pytest -v --tb=short --disable-warnings --maxfail=1 || { echo "❌ tests failed."; exit 1; }

unused-packages: ## Detect unused packages (deptry)
	@uv run deptry src

# ── Build / release ───────────────────────────────────────────────────────────

all: qa test build ## Run qa, tests and build

build: ## Build the package
	@uv build || { echo "❌ build failed."; exit 1; }
	@echo "✓ build complete"

clean: ## Remove build artifacts and caches
	@find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .ruff_cache \
		-o -name build -o -name dist -o -name "*.egg-info" \) -exec rm -rf {} + 2>/dev/null || true
	@find . -type f \( -name "*.pyc" -o -name ".coverage*" -o -name "coverage.xml" \) \
		-delete 2>/dev/null || true
	@echo "✓ clean complete"

zip: ## Zip git-tracked files into project.zip
	@git archive --format=zip --output=project.zip HEAD || { echo "❌ zip failed."; exit 1; }
	@echo "✓ project zipped"

# ── Utilities ─────────────────────────────────────────────────────────────────

spacy-models: ## Download required spaCy models
	@uv run python -m spacy download en_core_web_sm && echo "✓ spaCy models downloaded"

# ── AI tools ──────────────────────────────────────────────────────────────────

ai-hello-world: ## Run hello world tool
	@uv run ai-hello-world

ai-check-api-keys: ## Check API keys
	@uv run ai-check-api-keys

ai-commit: ## Generate commit messages
	@uv run ai-commit

ai-sample-assistant: ## Run sample assistant
	@KMP_DUPLICATE_LIB_OK=TRUE uv run ai-sample-assistant

ai-sample-agentic: ## Run sample agentic assistant
	@KMP_DUPLICATE_LIB_OK=TRUE uv run ai-sample-agentic
