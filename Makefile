# Author: Angel Martinez-Tenor, 2026. Adapted from https://github.com/angelmtenor/ds-template

VENV_DIR      := .venv
.DEFAULT_GOAL := help

# Export .env variables (includes SSL_CERT_FILE if configured)
ifneq (,$(wildcard .env))
    include .env
    export
endif

CYAN  := $(shell tput setaf 6 2>/dev/null)
RESET := $(shell tput sgr0 2>/dev/null)

.PHONY: help setup install check update qa ssl-check test unused-packages all build clean zip spacy-models generate run ai-hello-world ai-check-api-keys ai-commit ai-sample-assistant ai-sample-agentic ai-generate-data-model ai-app run-container build-container build-container-clean

# ── Help ──────────────────────────────────────────────────────────────────────

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS=":.*?## "}; {printf "  $(CYAN)%-22s$(RESET) %s\n", $$1, $$2}'

# ── Bootstrap ─────────────────────────────────────────────────────────────────

setup: ## Complete setup: venv, .env, generate settings, and verify environment
	@echo "🚀 Starting complete setup..."
	@if [ ! -f .env ] && [ -f .env.example ]; then echo "📝 Creating .env from .env.example..."; cp .env.example .env; fi
	@uv sync --extra optional && uv run pre-commit install && uv run python -m spacy download en_core_web_sm || { echo "❌ setup failed"; exit 1; }
	@$(MAKE) generate && uv run python check_full_env.py || { echo "⚠️  Environment check found issues."; }
	@echo "✓ Complete setup finished!"

install: ## Sync deps, install pre-commit hooks, and download spaCy models (run after cloning)
	@uv sync --extra optional     || { echo "❌ uv sync failed."; exit 1; }
	@uv run pre-commit install    || { echo "❌ pre-commit install failed."; exit 1; }
	@uv run python -m spacy download en_core_web_sm || { echo "⚠️  spaCy model download failed"; }
	@echo "✓ install complete"

check: qa test ## Verify code quality and run tests
	@echo "✓ Check complete"

update: ## Upgrade lockfile, sync deps & update pre-commit hooks
	@uv lock --upgrade            || { echo "❌ uv lock upgrade failed."; exit 1; }
	@uv sync --extra optional     || { echo "❌ uv sync failed."; exit 1; }
	@uv run pre-commit autoupdate || { echo "❌ pre-commit autoupdate failed."; exit 1; }
	@$(MAKE) generate
	@echo "✓ update complete"

# ── Dev workflow ──────────────────────────────────────────────────────────────

generate: ## Generate Pydantic data model from env_config.yaml
	@uv run ai-generate-data-model && uv run ruff format src/ai_circus/data_model.py

ssl-check: ## Detect and configure SSL CA bundle (for networks with SSL inspection)
	@uv run python scripts/ssl_setup.py

qa: ## Run all pre-commit checks (ruff, ruff-format, etc.)
	@$(MAKE) ssl-check
	@set -a && [ -f .env ] && . ./.env; uv run pre-commit run --all-files || { echo "❌ qa failed."; exit 1; }
	@echo "✓ qa complete"

test: ## Run test suite
	@uv run pytest -v --tb=short --disable-warnings --maxfail=1 || { echo "❌ tests failed."; exit 1; }

unused-packages: ## Detect unused packages (deptry)
	@uv run deptry src

# ── Build / release ───────────────────────────────────────────────────────────

all: clean setup check run ## Full end-to-end verification: clean, setup, check, and run

build: ## Build the package
	@uv build || { echo "❌ build failed."; exit 1; }
	@echo "✓ build complete"

build-container: ## Build the Docker image (uses layer cache)
	@DOCKER_BUILDKIT=1 docker build -t ai-circus .

build-container-clean: ## Force full rebuild of Docker image (no cache)
	@DOCKER_BUILDKIT=1 docker build --no-cache -t ai-circus .

run-container: build-container ## Build (cached) and run the Docker container
	@[ -f .env ] && docker run --rm -it --env-file .env ai-circus || docker run --rm -it ai-circus

clean: ## Remove build artifacts, caches, and .venv (with .env backup)
	@uv run python scripts/clean.py

zip: ## Zip git-tracked files into project.zip
	@git archive --format=zip --output=project.zip HEAD || { echo "❌ zip failed."; exit 1; }
	@echo "✓ project zipped"

# ── Utilities ─────────────────────────────────────────────────────────────────

spacy-models: ## Download required spaCy models
	@uv run python -m spacy download en_core_web_sm && echo "✓ spaCy models downloaded"

# ── AI tools ──────────────────────────────────────────────────────────────────

run: ## Run the main application (app.py)
	@uv run ai-app

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

ai-app: ## Run the main application (alias for 'make run')
	@$(MAKE) run
