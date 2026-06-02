from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CHECK_SCRIPT = ROOT / "scripts" / "check_readme_updated.py"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def _init_repo(repo: Path) -> str:
    (repo / "src").mkdir()
    (repo / "src" / "demo.py").write_text("print('hello')\n", encoding="utf-8")
    (repo / "README.md").write_text("# 中文\n", encoding="utf-8")
    (repo / "README_en.md").write_text("# English\n", encoding="utf-8")
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial")
    return _git(repo, "rev-parse", "HEAD")


def test_readme_check_fails_when_src_changes_without_readme(tmp_path):
    base = _init_repo(tmp_path)
    (tmp_path / "src" / "demo.py").write_text("print('changed')\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "change src")

    result = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), "--repo", str(tmp_path), "--base", base],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "README.md or README_en.md" in result.stdout


def test_readme_check_passes_when_src_and_readme_change(tmp_path):
    base = _init_repo(tmp_path)
    (tmp_path / "src" / "demo.py").write_text("print('changed')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# 中文\n\nUpdated.\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "change src and readme")

    result = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), "--repo", str(tmp_path), "--base", base],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "README updated" in result.stdout
