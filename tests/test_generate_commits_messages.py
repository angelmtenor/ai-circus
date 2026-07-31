"""Tests for the commit message generator tool.

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

import importlib
import subprocess
from pathlib import Path

import pytest

# ai_circus.tools.__init__ re-exports run_main as the name "generate_commits_messages",
# which shadows the submodule of the same name — import it directly to get the module.
gcm = importlib.import_module("ai_circus.tools.generate_commits_messages")


def test_read_styleguide_returns_file_contents_when_present(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """read_styleguide() should read styleguide.md from the current working directory."""
    (tmp_path / "styleguide.md").write_text("Custom guide", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    assert gcm.read_styleguide() == "Custom guide"


def test_read_styleguide_returns_default_when_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """read_styleguide() should fall back to the built-in default when styleguide.md is absent."""
    monkeypatch.chdir(tmp_path)

    assert "Conventional Commits" in gcm.read_styleguide()


def test_run_git_command_rejects_commands_outside_allow_list() -> None:
    """Commands not in the allow-list must never reach subprocess.run."""
    assert gcm.run_git_command(["git", "push", "--force"]) == ""


def test_run_git_command_runs_allowed_commands(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow-listed commands should be executed and their stdout returned."""

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(command, 0, stdout="M\tfile.py\n", stderr="")

    monkeypatch.setattr(gcm.subprocess, "run", fake_run)

    assert gcm.run_git_command(["git", "diff", "--name-status"]) == "M\tfile.py"


def test_get_changed_files_excludes_patterns_and_dedupes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Excluded file patterns should be dropped and files touched twice should be deduped."""

    def fake_run_git_command(command: list[str]) -> str:
        if command == ["git", "diff", "--cached", "--name-status"]:
            return "M\tsrc/app.py\nA\tuv.lock"
        if command == ["git", "diff", "--name-status"]:
            return "M\tsrc/app.py"
        if command == ["git", "ls-files", "--others", "--exclude-standard"]:
            return "notes.txt"
        if command[:2] == ["git", "diff"] and "--" in command:
            return "@@ -1 +1 @@\n-old\n+new"
        return ""

    monkeypatch.setattr(gcm, "run_git_command", fake_run_git_command)

    changes = gcm.get_changed_files()
    files = [c["file"] for c in changes]

    assert "uv.lock" not in files  # matches the *.lock$ exclusion pattern
    assert files.count("src/app.py") == 1  # staged + unstaged dedup to one entry
    assert "notes.txt" in files


def test_write_commit_script_writes_executable_script(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """write_commit_script() should render git add/commit commands for each group."""
    monkeypatch.chdir(tmp_path)
    groups = [{"message": "feat: Add thing", "files": ["a.py", "b.py"], "body": "Details"}]

    script_path = gcm.write_commit_script(groups)

    content = script_path.read_text(encoding="utf-8")
    assert 'git add "a.py"' in content
    assert 'git add "b.py"' in content
    assert 'git commit -m "feat: Add thing"' in content
    assert script_path.stat().st_mode & 0o777 == 0o755
