"""
check_full_env.py

Enhanced environment verification utility with beautiful, Makefile-aligned output.

Author: Angel Martinez-Tenor, 2025
"""

from __future__ import annotations

import os
import shutil
import sys
import tomllib
from argparse import ArgumentParser
from importlib import metadata
from pathlib import Path
from typing import Any, Protocol

from dotenv import dotenv_values, load_dotenv
from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

# ──────────────────────────────────────────────────────────────────────────────
# Define a minimal Printer protocol that both rich and fallback support
# ──────────────────────────────────────────────────────────────────────────────


class Printer(Protocol):
    """Protocol for a callable printer that supports both rich and fallback implementations."""

    def __call__(self, *objects: Any, sep: str = " ", end: str = "\n", **kwargs: Any) -> None:
        """Print the given objects with specified separators and end character."""
        ...


# ──────────────────────────────────────────────────────────────────────────────
# Rich imports with graceful fallback
# ──────────────────────────────────────────────────────────────────────────────

try:
    from rich.console import Console
    from rich.panel import Panel as RichPanel
    from rich.table import Table as RichTable

    console = Console()
    printer: Printer = console.print
    Panel: Any = RichPanel
    Table: Any = RichTable
except ImportError:  # Fallback if rich not installed
    console = None

    builtin_print = __builtins__["print"] if isinstance(__builtins__, dict) else __builtins__.print

    def fallback_printer(*objects: Any, sep: str = " ", end: str = "\n", **kwargs: Any) -> None:
        """Fallback printer that delegates to the builtin print."""
        # Ignore unused kwargs that rich supports but builtin doesn't
        kwargs.pop("style", None)
        kwargs.pop("justify", None)
        kwargs.pop("overflow", None)
        kwargs.pop("no_wrap", None)
        kwargs.pop("emoji", None)
        kwargs.pop("markup", None)
        kwargs.pop("highlight", None)
        kwargs.pop("width", None)
        kwargs.pop("height", None)
        kwargs.pop("crop", None)
        kwargs.pop("soft_wrap", None)
        kwargs.pop("new_line_start", None)
        builtin_print(*objects, sep=sep, end=end, **kwargs)

    printer = fallback_printer

    def panel(
        content: str | object,
        title: str | None = None,
        style: str = "bold cyan",
        **kwargs: object,
    ) -> str:
        """Fallback panel renderer used when `rich` is not installed."""
        del style, kwargs  # Unused in fallback
        content_str = str(content)
        border = "═" * (len(content_str) + 4)
        title_line = f" {title} " if title else ""
        return f"\n{border}\n{title_line}\n{border}\n  {content_str}  \n{border}\n"

    Panel = panel

    class FallbackTable:
        """Simple ASCII table fallback when rich is not available."""

        def __init__(self) -> None:
            """Initialize an empty fallback table."""
            self.rows: list[tuple[str, ...]] = []
            self.headers: list[str] = []

        def add_row(self, *cells: str) -> None:
            """Add a row of cells to the table."""
            self.rows.append(cells)

        def __str__(self) -> str:
            if not self.headers or not self.rows:
                return ""

            all_rows = [self.headers, *self.rows]
            widths = [max(len(str(cell)) for cell in col) for col in zip(*all_rows, strict=False)]

            header_line = " │ ".join(h.ljust(w) for h, w in zip(self.headers, widths, strict=False))
            sep = "─┼─".join("─" * w for w in widths)
            body = "\n".join(
                " │ ".join(str(c).ljust(w) for c, w in zip(row, widths, strict=False)) for row in self.rows
            )
            return f"{header_line}\n{sep}\n{body}"

    Table = FallbackTable


# ──────────────────────────────────────────────────────────────────────────────

parser = ArgumentParser(description="Check full project environment setup")
parser.add_argument("--verbose", "-v", action="store_true", help="Show all package details")
args = parser.parse_args()

issues_found = False


def log_success(msg: str) -> None:
    """Log a success message in green."""
    printer(f"[bold green]✅ {msg}[/bold green]")


def log_warning(msg: str) -> None:
    """Log a warning message in yellow and mark issues found."""
    global issues_found
    issues_found = True
    printer(f"[bold yellow]⚠️ {msg}[/bold yellow]")


def log_error(msg: str) -> None:
    """Log an error message in red and mark issues found."""
    global issues_found
    issues_found = True
    printer(f"[bold red]❌ {msg}[/bold red]")


def log_info(msg: str) -> None:
    """Log an informational message in cyan."""
    printer(f"[cyan]🔍 {msg}[/cyan]")


def section(title: str) -> None:
    """Print a titled section header."""
    printer(Panel(title, style="bold magenta", padding=(1, 2)))


# ──────────────────────────────────────────────────────────────────────────────


def check_virtual_environment(expected_venv_path: str = ".venv") -> None:
    """Check and report on the currently active Python virtual environment."""
    section("Virtual Environment")

    in_venv = hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
    current_prefix = Path(sys.prefix).resolve()
    expected_path = Path(expected_venv_path).resolve()

    printer(f"Active venv path: [dim]{current_prefix}[/dim]")

    if not in_venv:
        log_error("No virtual environment is activated")
        printer("   Run: [bold]source .venv/bin/activate[/bold] (macOS/Linux)")
        printer("   Or:  [bold].venv\\Scripts\\activate[/bold] (Windows)")
        return

    if current_prefix != expected_path:
        log_error(f"Wrong venv activated!\n   Expected: {expected_path}\n   Active:   {current_prefix}")
    else:
        log_success("Correct virtual environment is active")

    if shutil.which("uv"):
        log_success("uv is available in PATH")
    else:
        log_warning("uv not found in PATH")
        printer("   Install: https://docs.astral.sh/uv/getting-started/installation/")


def check_manual_installs(example_env_path: Path | str = ".env.example") -> None:
    """Check for CLI tools listed in `.env.example` under a marker."""
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

    section("Manual Installs (CLI Tools)")

    missing = [app for app in manual_installs if not shutil.which(app)]

    for app in manual_installs:
        if shutil.which(app):
            log_success(f"{app} found")
        else:
            log_warning(f"{app} not found in PATH")

    if missing:
        printer("   Consider installing missing tools or adding them to PATH.")


def summarize_value(value: str | None) -> str:
    """Return a redacted summary of an environment variable value."""
    if not value:
        return "[dim]<not set>[/dim]"
    if value.lower() in {"true", "false"}:
        return value.lower()
    return "****" + value[-4:] if len(value) >= 4 else "****"


def check_environment_variables(example_env_path: Path | str = ".env.example") -> None:
    """Validate environment variables against `.env.example`."""
    path = Path(example_env_path)
    if not path.exists():
        log_warning(f".env.example not found at {path}")
        return

    section("Environment Variables")

    example_vars = dotenv_values(path)
    required_keys: set[str] = set()

    with path.open("r", encoding="utf-8") as f:
        in_required = False
        for line in f:
            stripped = line.strip()
            if stripped.startswith("#") and "required" in stripped.lower():
                in_required = True
                continue
            if "=" in stripped and not stripped.startswith("#"):
                key = stripped.split("=", 1)[0].strip()
                if in_required:
                    required_keys.add(key)
                in_required = False

    table = Table()

    if console:  # Rich Table
        table.add_row("Key", "Value", "Status", style="bold")
        table.show_header = True
    else:  # FallbackTable
        table.headers = ["Key", "Value", "Status"]

    for key in sorted(example_vars.keys()):
        current = os.getenv(key)
        summary = summarize_value(current)
        example_val = example_vars.get(key) or ""
        placeholder = example_val.strip("\"'")

        if key in required_keys:
            if current is None:
                status = "[red]Missing (required)[/red]"
                log_error(f"{key} is required but not set")
            elif current == placeholder:
                status = "[yellow]Placeholder value[/yellow]"
                log_warning(f"{key} still has example/placeholder value")
            else:
                status = "[green]Set[/green]"
        else:
            status = "[green]Set[/green]" if current else "[dim]Optional[/dim]"

        table.add_row(key, summary, status)

    printer(table)


def check_python_packages(pyproject_path: str = "pyproject.toml") -> None:
    """Check that packages declared in `pyproject.toml` are installed."""
    p = Path(pyproject_path)
    if not p.exists():
        log_error(f"{pyproject_path} not found")
        return

    with p.open("rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    requires_python = project.get("requires-python", ">=3.11")
    dependencies: list[str] = project.get("dependencies", [])

    current_version = Version(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    python_ok = current_version in SpecifierSet(requires_python)

    section("Python Packages")

    status = "[green]OK[/green]" if python_ok else "[red]FAIL[/red]"
    printer(f"Python version: {current_version} → requires-python: {requires_python} → {status}")

    if not dependencies:
        log_info("No dependencies declared in pyproject.toml")
        return

    table = Table()

    if console:
        table.add_row("Package", "Required", "Installed", "Status", style="bold")
        table.show_header = True
    else:
        table.headers = ["Package", "Required", "Installed", "Status"]

    problems = 0
    for dep_str in dependencies:
        try:
            req = Requirement(dep_str)
            name = req.name
            specifier = str(req.specifier) or "(any)"
        except InvalidRequirement:
            name = dep_str.split()[0] if dep_str else "unknown"
            specifier = "(invalid)"

        try:
            installed_ver = metadata.version(name)
            if specifier not in {"(any)", "(invalid)"} and Version(installed_ver) in SpecifierSet(specifier):
                status = "[green]OK[/green]"
            else:
                status = "[yellow]Version mismatch[/yellow]"
                problems += 1
        except metadata.PackageNotFoundError:
            installed_ver = "[dim]Not installed[/dim]"
            status = "[red]Missing[/red]"
            problems += 1

        if args.verbose or status != "[green]OK[/green]":
            table.add_row(name, specifier, installed_ver, status)

    has_rows = (console and getattr(table, "row_count", 0) > 0) or (not console and table.rows)
    if has_rows:
        printer(table)

    if problems == 0:
        log_success("All required packages are installed and compatible")
    else:
        log_warning(f"{problems} package issue(s) found")


# ──────────────────────────────────────────────────────────────────────────────


def main() -> None:
    """Run the full environment checks and print a summary panel."""
    printer(Panel("AI Circus Environment Check", style="bold blue", padding=(1, 3)))

    check_virtual_environment()
    check_manual_installs()
    load_dotenv()
    check_environment_variables()
    check_python_packages()

    printer("\n" + "═" * 60)
    if not issues_found:
        printer(Panel("[bold green]✅ All checks passed! Environment is ready.[/bold green]", style="green"))
    else:
        printer(Panel("[bold yellow]⚠️  Some issues were found. Review warnings above.[/bold yellow]", style="yellow"))


if __name__ == "__main__":
    main()
