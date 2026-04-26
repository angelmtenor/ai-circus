"""
generate_commit_messages.py
--------------------------

Tool to generate conventional commit messages for uncommitted changes in a Git repository
using an LLM. Analyzes all changes together for intelligent grouping into logical commits.

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

import asyncio
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ai_circus.core.logger import get_logger
from ai_circus.models import get_llm

EXCLUDED_PATTERNS = [r"\.ipynb$", r"\.lock$", r"\.json$", r"\.log$", r"^temp_output/"]

logger = get_logger(__name__)


def read_styleguide() -> str:
    """Read styleguide.md or return default Conventional Commits guide."""
    styleguide_path = Path("styleguide.md")
    default = (
        "Follow Conventional Commits specification[](https://www.conventionalcommits.org).\n"
        "Use types: feat, fix, docs, style, refactor, test, perf, build, ci, chore.\n"
        "Format: <type>[optional scope]: <description>\n"
        "Use imperative present tense. Description <= 72 characters.\n"
        "Optional body for detailed explanation.\n"
        "Group related changes into cohesive commits."
    )
    return styleguide_path.read_text(encoding="utf-8") if styleguide_path.exists() else default


def run_git_command(command: list[str]) -> str:
    """Run a Git command safely using a trusted allow-list and return stdout."""
    # Allow specific git commands used in this tool (including per-file diffs with -- file)
    allowed_bases = {
        ("git", "diff", "--cached", "--name-status"),
        ("git", "diff", "--name-status"),
        ("git", "ls-files", "--others", "--exclude-standard"),
        ("git", "diff", "--cached"),
        ("git", "diff"),
    }

    # Extract base command ignoring file paths after --
    if "--" in command:
        base_idx = command.index("--")
        base_cmd = tuple(command[:base_idx])
    else:
        base_cmd = tuple(command)

    if base_cmd not in allowed_bases:
        logger.error(f"Disallowed git command attempted: {' '.join(command)}")
        return ""

    try:
        result = subprocess.run(  # noqa: S603  # Command is allow-listed
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=Path.cwd(),
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {' '.join(command)} | {e.stderr.strip()}")
        return ""


def get_changed_files() -> list[dict[str, str]]:
    """Collect staged, unstaged, and untracked changes with truncated diffs."""
    changes: list[dict[str, str]] = []

    # Staged changes
    staged = run_git_command(["git", "diff", "--cached", "--name-status"])
    for line in staged.splitlines():
        if "\t" not in line:
            continue
        status, file_path = line.split("\t", 1)
        if any(re.search(p, file_path) for p in EXCLUDED_PATTERNS):
            continue
        diff = run_git_command(["git", "diff", "--cached", "--", file_path])
        diff = "\n".join(diff.splitlines()[:20]) + ("\n... (truncated)" if diff else "")
        changes.append({"file": file_path, "status": status, "diff": diff or "No changes in diff"})

    # Unstaged changes
    unstaged = run_git_command(["git", "diff", "--name-status"])
    for line in unstaged.splitlines():
        if "\t" not in line:
            continue
        status, file_path = line.split("\t", 1)
        if any(re.search(p, file_path) for p in EXCLUDED_PATTERNS):
            continue
        diff = run_git_command(["git", "diff", "--", file_path])
        diff = "\n".join(diff.splitlines()[:20]) + ("\n... (truncated)" if diff else "")
        changes.append({"file": file_path, "status": status, "diff": diff or "No changes in diff"})

    # Untracked files
    untracked = run_git_command(["git", "ls-files", "--others", "--exclude-standard"]).splitlines()
    for file_path in untracked:
        if not file_path or any(re.search(p, file_path) for p in EXCLUDED_PATTERNS):
            continue
        changes.append({"file": file_path, "status": "??", "diff": "New untracked file"})

    unique: dict[str, dict[str, str]] = {}
    for change in changes:
        unique[change["file"]] = change

    logger.debug(f"Detected {len(unique)} unique changes")
    return list(unique.values())


async def generate_commit_groups(changes: list[dict[str, str]], styleguide: str) -> list[dict[str, Any]]:
    """Generate grouped conventional commit messages by analyzing all changes at once."""
    if not changes:
        logger.info("No changes detected")
        return []

    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert in Conventional Commits. Analyze ALL file changes below and group them into logical,
        cohesive commits. Related changes should be combined.

        **Style Guide**:
        {styleguide}

        **All Changes**:
        {changes_summary}

        **Output Format**:
        Respond ONLY with a valid JSON array:
        [
          {{
            "group": "<type> (e.g., feat, fix, refactor, docs, chore)",
            "scope": "<optional scope>",
            "message": "<type>[scope]: <description>",
            "body": "<optional longer explanation>",
            "files": ["file1.py", "file2.py", ...]
          }},
          ...
        ]

        Rules:
        - Imperative present tense
        - Description <= 72 chars
        - Valid JSON only - no markdown or extra text
        """
    )

    changes_summary = "\n\n".join(f"File: {c['file']}\nStatus: {c['status']}\nDiff:\n{c['diff']}" for c in changes)

    chain = prompt | llm | StrOutputParser()
    raw = await chain.ainvoke({"styleguide": styleguide, "changes_summary": changes_summary})

    logger.info(f"Raw LLM output:\n{raw}")

    json_match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not json_match:
        logger.error("No JSON array found in LLM response")
        return []

    try:
        groups = json.loads(json_match.group(0))
        if not isinstance(groups, list):
            logger.error("Parsed output is not a list")
            return []
        return groups
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {e}")
        return []


def write_commit_script(groups: list[dict[str, Any]]) -> Path:
    """Generate executable bash script with git commands."""
    script_path = Path("temp_output/commit_commands.sh")
    script_path.parent.mkdir(parents=True, exist_ok=True)

    with script_path.open("w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n\nset -e\n\n")
        for i, group in enumerate(groups, 1):
            f.write(f"# Commit {i}: {group.get('message', 'Untitled')}\n")
            if body := group.get("body"):
                f.write(f"# {body.replace('\n', '\n# ')}\n")
            for file in group.get("files", []):
                f.write(f'git add "{file}"\n')
            msg = group.get("message", "Update files")
            f.write(f'git commit -m "{msg}"\n\n')

    script_path.chmod(0o755)
    return script_path


def execute_commands(script_path: Path) -> None:
    """Display proposed commits and handle user decision."""
    logger.info(f"Generated commit script: {script_path}")

    logger.info("\n" + "=" * 60)
    logger.info("PROPOSED COMMITS")
    logger.info("=" * 60)
    with script_path.open("r", encoding="utf-8") as f:
        logger.info(f.read())
    logger.info("=" * 60)

    while True:
        choice = input("\nExecute script? (yes/no/edit): ").strip().lower()
        if choice == "yes":
            try:
                git_path = shutil.which("git")
                bash_path = shutil.which("bash")
                if not git_path or not bash_path:
                    raise RuntimeError("git or bash not found in PATH")

                # Safe execution with full paths from trusted PATH
                subprocess.run([git_path, "reset"], check=True, cwd=Path.cwd())  # noqa: S603
                subprocess.run([bash_path, str(script_path)], check=True, cwd=Path.cwd())  # noqa: S603
                logger.info("Commits executed successfully")
                break
            except subprocess.CalledProcessError as e:
                logger.error(f"Execution failed: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                break
        elif choice == "no":
            logger.info(f"Script saved at {script_path} for manual execution")
            break
        elif choice == "edit":
            logger.info(f"Please edit {script_path} manually and run it")
            break
        else:
            logger.warning("Invalid input. Please enter 'yes', 'no', or 'edit'")


async def main() -> None:
    """Main entry point: detect changes, generate commits, and offer execution."""
    styleguide = read_styleguide()
    changes = get_changed_files()
    if not changes:
        logger.info("No changes to commit")
        return

    groups = await generate_commit_groups(changes, styleguide)
    if not groups:
        logger.info("No valid commit groups generated")
        return

    script_path = write_commit_script(groups)
    execute_commands(script_path)


def run_main() -> None:
    """Synchronous wrapper for running as a script or tool."""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
