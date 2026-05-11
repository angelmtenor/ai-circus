# ai-circus

A building block for generative AI tool applications with state-of-the-art performance.

---

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)
![PyPI Package](https://img.shields.io/badge/Package%20Version-0.1.1-green?style=for-the-badge)
![Supported Python Versions](https://img.shields.io/badge/Supported%20Python%20Versions-3.14%2B-blue?style=for-the-badge)

---

## 🚀 Quick Start

Get up and running in seconds after cloning the repository:

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

---

## Contributing

- Please refer to [AGENTS.md](AGENTS.md) for strict architectural and testing guidelines.
- Review the [Style Guide](styleguide.md) for commit message and coding conventions.
- See [Contributing Guidelines](CONTRIBUTING.md) for the workflow and submission process.
- Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).
