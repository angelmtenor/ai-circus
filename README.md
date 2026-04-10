# ai-circus

A building block for generative AI tool applications with state-of-the-art performance.

---

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)
![PyPI Package](https://img.shields.io/badge/Package%20Version-0.1.1-green?style=for-the-badge)
![Supported Python Versions](https://img.shields.io/badge/Supported%20Python%20Versions-3.13%2B-blue?style=for-the-badge)

---

## Work in Progress

This project is under active development. Features and APIs are subject to change.

Planned work:

- OpenSearch integration for vector storage
- Agent framework integration (LangChain, OpenAI SDK, etc.)
- MCP (Model Context Protocol) support and examples
- Agentic & MCP connectivity examples

---

## Tools and Frameworks

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=FFD43B)
![uv](https://img.shields.io/badge/uv-4baaaa?style=for-the-badge&logo=github)
![Ruff](https://img.shields.io/badge/Ruff-000000?style=for-the-badge&logo=ruff&logoColor=white)
![Pyrefly](https://img.shields.io/badge/Pyrefly-61DAFB?style=for-the-badge&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9DFF?style=for-the-badge&logo=pytest&logoColor=white)
![Pre-commit](https://img.shields.io/badge/Pre--commit-FDA50F?style=for-the-badge&logo=pre-commit&logoColor=white)

---

## Package Usage

Requires Python 3.13+. Using a virtual environment is strongly recommended.

```bash
pip install ai-circus
# or
uv add ai-circus
```

Set up your environment:

```bash
cp .env.example .env
# Edit .env and fill in the required API keys
```

Available CLI tools:

- `ai-hello-world` — simple hello world smoke test
- `ai-check-api-keys` — validates API keys in your `.env` (OpenAI, Google, Tavily)
- `ai-commit` — generates and commits a message for your current changes
- `ai-sample-assistant` — runs the sample assistant demo

---

## Development Setup

### One-time system setup (Debian/Ubuntu)

```bash
sudo ./.devcontainer/setup_sudo.sh   # configures sudo, installs base packages
./.devcontainer/setup_user.sh        # installs uv, pre-commit, configures shell
source ~/.bashrc                     # apply shell changes
```

### Project setup

After cloning, install dependencies and pre-commit hooks:

```bash
make install
```

Then verify the full environment (venv, uv, packages, env vars):

```bash
make check
```

### Common workflows

| Command | Description |
|---|---|
| `make install` | Sync deps and install pre-commit hooks |
| `make check` | Verify full environment via `check_full_env.py` |
| `make update` | Upgrade lockfile, sync deps, update pre-commit hooks |
| `make qa` | Run all pre-commit checks (ruff, ruff-format, pyrefly, checkmake, etc.) |
| `make test` | Run the pytest suite |
| `make all` | Run qa + test + build |
| `make build` | Build the package |
| `make clean` | Remove build artifacts and caches |
| `make unused-packages` | Detect unused dependencies via deptry |
| `make spacy-models` | Download required spaCy models |
| `make zip` | Archive git-tracked files into `project.zip` |

---

## Contributing

- Review the [Style Guide](styleguide.md) for commit message and coding conventions
- See [Contributing Guidelines](CONTRIBUTING.md) for the workflow and submission process
- Please follow the [Code of Conduct](CODE_OF_CONDUCT.md)
