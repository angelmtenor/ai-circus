# Author: Angel Martinez-Tenor, 2025. Adapted from https://github.com/angelmtenor/ds-template

VENV_DIR      := .venv
.DEFAULT_GOAL := help

CYAN  := $(shell tput setaf 6 2>/dev/null)
RESET := $(shell tput sgr0 2>/dev/null)

.PHONY: help all check-uv check-venv check-full-env update \
        qa build unused-packages zip spacy-models \
        hello-world check-api-keys commit sample-assistant
.PHONY: test
.PHONY: clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS=":.*?## "}; {printf "  $(CYAN)%-22s$(RESET) %s\n", $$1, $$2}'

all: qa test build ## Run QA, tests and build

check-uv: ## Verify uv is installed, install if missing
	@command -v uv >/dev/null 2>&1 && echo "✓ uv $$(uv --version)" && exit 0; \
	echo "→ uv not found. Installing..."; \
	case "$$(uname)" in Darwin|Linux) curl -LsSf https://astral.sh/uv/install.sh | sh ;; \
	*) echo "Windows: irm https://astral.sh/uv/install.ps1 | iex" ;; esac

check-venv: check-uv ## Verify correct virtual environment is active
	@[ -n "$$VIRTUAL_ENV" ] || { echo "❌ No venv active. Run: source $(VENV_DIR)/bin/activate"; exit 1; }
	@[ "$$VIRTUAL_ENV" = "$(PWD)/$(VENV_DIR)" ] || { \
		echo "❌ Wrong venv: $$VIRTUAL_ENV — expected $(PWD)/$(VENV_DIR). Run: deactivate"; exit 1; }
	@uv lock --locked && echo "✓ venv active"

check-full-env: ## Check full environment setup via check_full_env.py
	@python check_full_env.py || { echo "❌ check_full_env.py failed."; exit 1; }
	@echo "✓ full environment correct"

update: check-venv ## Upgrade lockfile, sync deps & update pre-commit hooks
	@uv lock --upgrade            || { echo "❌ uv lock upgrade failed."; exit 1; }
	@uv sync --extra optional     || { echo "❌ uv sync failed."; exit 1; }
	@uv run pre-commit autoupdate || { echo "❌ pre-commit autoupdate failed."; exit 1; }
	@echo "✓ update complete"

qa: ## Run all pre-commit checks (includes ruff and ruff-format)
	@uv run pre-commit run --all-files || { echo "❌ QA failed."; exit 1; }
	@echo "✓ QA complete"

unused-packages: ## Detect unused packages (deptry)
	@uv run deptry src

test: ## Run test suite
	@uv run pytest -v --tb=short --disable-warnings --maxfail=1 || { echo "❌ tests failed."; exit 1; }

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

.PHONY: spacy-models
spacy-models: ## Download required spaCy models
	@uv run python -m spacy download en_core_web_sm && echo "✓ spaCy models downloaded"


ai-hello-world: ## Run hello world tool
	@uv run ai-hello-world

ai-check-api-keys: ## Check API keys
	@uv run ai-check-api-keys

ai-commit: ## Generate commit messages
	@uv run ai-commit

ai-sample-assistant: ## Run sample assistant
	@uv run ai-sample-assistant
