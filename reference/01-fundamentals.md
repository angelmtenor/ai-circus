# 01 — Fundamentals & Toolchain (Language-Agnostic Basics)

The baseline tools every project in this repo is built on, independent of ML or GenAI
specifics. Get comfortable with these before moving on to
[02-software-engineering.md](02-software-engineering.md).

## Python

* [W3Schools](https://www.w3schools.com/) — quick syntax/reference lookups.
* **Package manager: uv** (installer/resolver) — [uv Documentation](https://docs.astral.sh/uv)
* **Linter & formatter: ruff** (fast, replaces black/flake8/isort) — [ruff Documentation](https://docs.astral.sh/ruff)

## Unix / Shell

* [TutorialsPoint UNIX Quick Guide](https://www.tutorialspoint.com/unix/unix-quick-guide.htm)

## VS Code

* [VS Code Documentation](https://code.visualstudio.com/docs)

## Docker

* [Docker Install Guide (Ubuntu)](https://docs.docker.com/engine/install/ubuntu/)

## Build Automation: Makefile

* [Creating a Python Makefile – Earthly Blog](https://earthly.dev/blog/python-makefile/) —
  covers targets, `.PHONY`, variables, and `venv`/test/lint/clean rules using Python examples
  (not C/C++).

## QA / Code Quality: pre-commit

* [pre-commit Documentation](https://pre-commit.com) — manages and runs hooks (ruff, formatting,
  secret detection, etc.) before every commit.

## Project Scaffolding: cookiecutter

* [cookiecutter Documentation](https://cookiecutter.readthedocs.io/)
* Use reproducible templates that bundle pre-commit, a Makefile, and unified tooling out of
  the box, so every new project starts standardized instead of copy-pasted.
* **This repo (ai-circus) is being groomed into exactly such a template** — see
  [00-itinerary.md](00-itinerary.md).
