# Author: Angel Martinez-Tenor, 2025. Adapted from https://github.com/angelmtenor/ds-template

VENV_DIR      := .venv
.DEFAULT_GOAL := help

CYAN  := $(shell tput setaf 6 2>/dev/null)
RESET := $(shell tput sgr0 2>/dev/null)

.PHONY: help all setup update qa test build unused-packages \
        spacy-models zip clean \
        ai-hello-world ai-check-api-keys ai-commit ai-sample-assistant

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS=":.*?## "}; {printf "  $(CYAN)%-22s$(RESET) %s\n", $$1, $$2}'

all: qa test build ## Run QA, tests and build

setup: ## Verify full environment (venv, uv, packages, env vars)
	@uv run python check_full_env.py || { echo "❌ Environment check failed."; exit 1; }
	@echo "✓ Environment ready"

update: ## Upgrade lockfile, sync deps & update pre-commit hooks
	@uv lock --upgrade            || { echo "❌ uv lock upgrade failed."; exit 1; }
	@uv sync --extra optional     || { echo "❌ uv sync failed."; exit 1; }
	@uv run pre-commit autoupdate || { echo "❌ pre-commit autoupdate failed."; exit 1; }
	@echo "✓ update complete"

qa: ## Run all pre-commit checks (includes ruff, ruff-format, etc.)
	@uv run pre-commit run --all-files || { echo "❌ QA failed."; exit 1; }
	@echo "✓ QA complete"

test: ## Run test suite
	@uv run pytest -v --tb=short --disable-warnings --maxfail=1 || { echo "❌ tests failed."; exit 1; }

build: ## Build the package
	@uv build || { echo "❌ build failed."; exit 1; }
	@echo "✓ build complete"

unused-packages: ## Detect unused packages (deptry)
	@uv run deptry src

spacy-models: ## Download required spaCy models
	@uv run python -m spacy download en_core_web_sm && echo "✓ spaCy models downloaded"

zip: ## Zip git-tracked files into project.zip
	@git archive --format=zip --output=project.zip HEAD || { echo "❌ zip failed."; exit 1; }
	@echo "✓ project zipped"

clean: ## Remove build artifacts and caches
	@find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .ruff_cache \
		-o -name build -o -name dist -o -name "*.egg-info" \) -exec rm -rf {} + 2>/dev/null || true
	@find . -type f \( -name "*.pyc" -o -name ".coverage*" -o -name "coverage.xml" \) \
		-delete 2>/dev/null || true
	@echo "✓ clean complete"

ai-hello-world: ## Run hello world tool
	@uv run ai-hello-world

ai-check-api-keys: ## Check API keys
	@uv run ai-check-api-keys

ai-commit: ## Generate commit messages
	@uv run ai-commit

ai-sample-assistant: ## Run sample assistant
	@uv run ai-sample-assistant
