# ai-circus

A building block for generative AI tool applications with state-of-the-art performance.

---

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)
![PyPI Package](https://img.shields.io/badge/Package%20Version-0.1.1-green?style=for-the-badge)
![Supported Python Versions](https://img.shields.io/badge/Supported%20Python%20Versions-3.14%2B-blue?style=for-the-badge)

---

## 🖥️ Prerequisites: Development Environment

Production is Linux, so development should be too — this repo targets **Ubuntu 26.04
(minimal)**, whichever way you provision it:

- **macOS / native Linux:** already Unix-based — skip ahead to Quick Start.
- **Windows:** use **WSL** ([install guide](https://learn.microsoft.com/en-us/windows/wsl/install)).
- **Remote VM** (AWS/Azure/GCP/on-prem): provision an Ubuntu 26.04 base and connect over SSH.
- **VS Code Dev Container:** open this folder in VS Code and let it build `.devcontainer/Dockerfile`.

Once you're on an Ubuntu 26.04 machine or session (WSL, native Linux, or remote VM — not needed
for Dev Containers, which run this automatically), provision it with this repo's setup scripts:

```bash
sudo ./.devcontainer/setup_sudo.sh   # one-time root setup: packages, timezone, optional GPU/CUDA
source .devcontainer/setup_user.sh   # per-user setup: git config, uv, Node via nvm, shell prompt (must be sourced)
```

Both scripts are idempotent (safe to re-run). See
[reference/01-fundamentals.md](reference/01-fundamentals.md) for the full rationale and options.

---

## 🚀 Quick Start

Once your environment is ready, get the project up and running in seconds after cloning the
repository:

```bash
make setup    # Initialize venv, .env, generate settings, and verify environment
make check    # Run QA checks (linting) and tests
make run      # Run the main hello world application
```

To verify everything end-to-end before a commit:
```bash
make all      # clean -> setup -> check -> run
```

---

## Work in Progress

This project is under active development. Features and APIs are subject to change.

Implemented:
- Centralized Pydantic configuration (`settings.yaml`)
- Validated environment setup (`make setup`)
- Simplified LLM/Embedding initialization (`ai_circus.get_llm`)

Planned:
- OpenSearch integration for vector storage
- Agent framework integration (LangChain, OpenAI SDK, etc.)
- MCP (Model Context Protocol) support and examples

---

## Tools and Frameworks

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=FFD43B)
![uv](https://img.shields.io/badge/uv-4baaaa?style=for-the-badge&logo=github)
![Ruff](https://img.shields.io/badge/Ruff-000000?style=for-the-badge&logo=ruff&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9DFF?style=for-the-badge&logo=pytest&logoColor=white)
![Pre-commit](https://img.shields.io/badge/Pre--commit-FDA50F?style=for-the-badge&logo=pre-commit&logoColor=white)

---

## Configuration

The project uses a single source of truth for settings defined in `settings.yaml`.

1. Run `make setup` to initialize your `.env` file from `.env.example`.
2. Edit `.env` to fill in your `OPENAI_API_KEY` and other optional keys.
3. The application will automatically validate these at runtime using Pydantic.

---

## Common Workflows

| Command | Description |
|---|---|
| `make clean` | Remove `.venv`, caches, and artifacts (with `.env` backup) |
| `make setup` | Full environment initialization and verification |
| `make check` | Run `qa` (linting) and `test` (unit tests) |
| `make run` | Execute the main application |
| `make qa` | Run pre-commit hooks (ruff, etc.) |
| `make test` | Run the pytest suite |
| `make all` | Full end-to-end verification pipeline |
| `make update` | Upgrade lockfile, sync deps, update pre-commit hooks |

### AI Tools

| Command | Description |
|---|---|
| `make ai-hello-world` | Basic demo: log system info and greet using your configured LLM provider (no LLM call) |
| `make ai-check-api-keys` | Validate that configured API keys actually work |
| `make ai-commit` | Generate a commit message from staged changes |
| `make ai-sample-assistant` | Run the sample single-turn assistant |
| `make ai-sample-agentic` | Run the sample tool-using agentic assistant |
| `make ai-app` | Run the main application (alias for `make run`) |

Each target is a thin wrapper around a `uv run` console script — they're declared under
`[project.scripts]` in [pyproject.toml](pyproject.toml) and can be run directly without `make`,
e.g. `uv run ai-hello-world`.

---

## 📚 Learn More

For the reasoning behind this stack and structure — dev environment, tooling, software
engineering practices, ML, and GenAI — see the reference notes starting at
[reference/00-itinerary.md](reference/00-itinerary.md).

---

## Contributing

- Please refer to [AGENTS.md](AGENTS.md) for strict architectural and testing guidelines.
- Review the [Style Guide](styleguide.md) for commit message and coding conventions.
- See [Contributing Guidelines](CONTRIBUTING.md) for the workflow and submission process.
- Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).
