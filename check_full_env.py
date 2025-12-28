"""
check_full_env.py

Utility script to verify the environment setup.

Checks:
- Virtual environment activation and path
- Python version compatibility (from pyproject.toml)
- Required Python packages
- Environment variables (against .env.example)
- Manually installed CLI tools (e.g., uv, node, etc.)

Original: Langchain Community: https://github.com/langchain-ai/lca-lc-foundations, 2025
Adapted by: Angel Martinez-Tenor, 2025
"""

from __future__ import annotations

import os
import shutil
import sys
import tomllib
from importlib import metadata
from pathlib import Path
from typing import Any

from dotenv import dotenv_values, load_dotenv
from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from ai_circus.core.logger import configure_logger

# Configure logger early
logger = configure_logger(level="INFO")
log = logger.info
warn = logger.warning
error = logger.error


def summarize_value(value: str | None) -> str:
    """Safely summarize sensitive values (API keys, booleans)."""
    if not value:
        return "<not set>"
    lower = value.lower()
    if lower in {"true", "false"}:
        return lower
    return "****" + value[-4:] if len(value) >= 4 else "****"


def check_manual_installs(example_env_path: Path | str = ".env.example") -> None:
    """Check availability of manually installed tools listed in .env.example."""
    path = Path(example_env_path)
    if not path.exists():
        return

    manual_installs: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("# Manual installs for checking:"):
                apps_part = stripped.split(":", 1)[1].strip()
                manual_installs = [app.strip() for app in apps_part.split(",") if app.strip()]
                break

    if not manual_installs:
        return

    log("Manual Installs Check:")
    found = []
    missing = []

    for app in manual_installs:
        if shutil.which(app):
            found.append(app)
        else:
            missing.append(f"Warning: {app} not found in PATH")

    for item in found:
        log(item)
    for item in missing:
        warn(item)

    if missing:
        warn("Consider installing missing tools or adding them to your PATH.")
    log("")  # empty line for spacing


def check_environment_variables(example_env_path: Path | str = ".env.example") -> None:
    """Compare current env vars with .env.example, highlighting unset or placeholder values."""
    path = Path(example_env_path)
    if not path.exists():
        warn(f".env.example not found at {path}. Skipping environment variable check.")
        return

    # Identify required keys (marked with "required" in comments above section)
    required_keys: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    in_required_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            in_required_section = "required" in stripped.lower()
            continue

        if "=" in stripped and not stripped.startswith("#"):
            key = stripped.split("=", 1)[0].strip()
            value = stripped.split("=", 1)[1].strip().strip("\"'")
            if in_required_section:
                required_keys[key] = value

    # Load all keys from .env.example
    example_vars = dotenv_values(path)
    issues: list[str] = []

    log("Environment Variables Check:")
    for key in sorted(example_vars.keys()):
        current = os.getenv(key)
        summary = summarize_value(current)
        log(f"{key}={summary}")

        if key in required_keys:
            example_val = required_keys[key]
            if current is None:
                issues.append(f"Warning: {key} is required but not set")
            elif current == example_val:
                issues.append(f"Warning: {key} still has placeholder/example value")

    if issues:
        log("")  # spacing
        log("Issues found:")
        for issue in issues:
            warn(issue)
    log("")  # final spacing


def check_virtual_environment(expected_venv_path: str = ".venv") -> None:
    """Verify that the correct virtual environment is activated and display its path."""
    log("Virtual Environment Check:")

    in_venv = hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)

    current_prefix = Path(sys.prefix).resolve()
    expected_path = Path(expected_venv_path).resolve()

    # Display the active virtual environment path once, prominently
    log(f"Active virtual environment path: {current_prefix}")

    if not in_venv:
        warn("Virtual environment is not activated")
        warn("   -> Run: source .venv/bin/activate   (macOS/Linux)")
        warn("   -> Or: .venv\\Scripts\\activate     (Windows)")
    elif current_prefix != expected_path:
        warn(f"Activated venv ({current_prefix}) does not match expected ({expected_path})")
    else:
        log("Success: Virtual environment is properly activated")

    # Check for uv (recommended tool)
    if shutil.which("uv"):
        log("Success: uv is available")
    else:
        log("Info: 'uv' not found")
        log("   Install: https://docs.astral.sh/uv/getting-started/installation/")
    log("")  # spacing


def _format_table(rows: list[list[str]], headers: list[str]) -> str:
    """Simple left-aligned table formatting."""
    widths = [max(len(str(cell)) for cell in col) for col in zip(*rows, headers, strict=True)]
    header_row = " | ".join(h.ljust(w) for h, w in zip(headers, widths, strict=True))
    separator = " | ".join("-" * w for w in widths)
    body = "\n".join(" | ".join(str(c).ljust(w) for c, w in zip(row, widths, strict=True)) for row in rows)
    return f"{header_row}\n{separator}\n{body}"


def check_python_packages(pyproject_path: str = "pyproject.toml", verbose: bool = False) -> None:
    """Check Python version and package dependencies against pyproject.toml (without path column)."""
    p = Path(pyproject_path)
    if not p.exists():
        error(f"{pyproject_path} not found in {p.cwd()}")
        return

    with p.open("rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    requires_python = project.get("requires-python", ">=3.11")
    dependencies: list[str] = project.get("dependencies", [])

    current_version = Version(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    python_ok = current_version in SpecifierSet(requires_python)

    status = "OK" if python_ok else "FAIL"
    log(f"Python {current_version} -> requires-python: {requires_python} -> {status}")

    if not dependencies:
        if verbose or not python_ok:
            log("No dependencies listed in pyproject.toml")
            log(f"Executable: {sys.executable}")
        return

    results: list[dict[str, Any]] = []
    problems: list[dict[str, Any]] = []

    for dep_str in dependencies:
        try:
            req = Requirement(dep_str)
            name = req.name
            specifier = str(req.specifier) or "(any)"
        except InvalidRequirement:
            name = dep_str.split()[0] if dep_str else "unknown"
            specifier = "(invalid)"

        record = {
            "package": name,
            "required": specifier,
            "installed": "-",
            "status": "Error: Missing",
        }

        try:
            installed_ver = metadata.version(name)
            record["installed"] = installed_ver

            if specifier not in {"(any)", "(invalid)"} and any(op in specifier for op in "<>="):
                if Version(installed_ver) in SpecifierSet(specifier):
                    record["status"] = "OK"
                else:
                    record["status"] = "Warning: Version mismatch"
            else:
                record["status"] = "OK"
        except metadata.PackageNotFoundError:
            pass

        results.append(record)
        if record["status"] != "OK":
            problems.append(record)

    should_print = verbose or problems or not python_ok
    if should_print:
        rows = [
            [
                r["package"],
                r["required"],
                r["installed"],
                r["status"],
            ]
            for r in results
        ]

        table = _format_table(rows, ["Package", "Required", "Installed", "Status"])
        log(table)

        if problems:
            log("")  # spacing
            log("Package Issues:")
            for prob in problems:
                warn(
                    f"- {prob['package']}: {prob['status']} "
                    f"(required {prob['required']}, installed {prob['installed']})"
                )

        log(f"\nEnvironment: {sys.executable}")

    else:
        log("Success: All Python packages are correctly installed and compatible")


def main() -> None:
    """Run all environment checks."""
    log("AI Circus Environment Check")
    log("=" * 40)

    check_virtual_environment()
    check_manual_installs()
    load_dotenv()  # Load .env if present
    check_environment_variables()
    check_python_packages(verbose=True)

    log("Check complete.")


if __name__ == "__main__":
    main()
