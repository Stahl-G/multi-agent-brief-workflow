#!/usr/bin/env python
"""Cross-platform README update check for source changes.

This script is intentionally small and dependency-free so it can run from
PowerShell, bash, pre-push hooks, and GitHub Actions.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


README_FILES = ("README.md", "README_en.md")


def git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def changed_files(base: str, head: str, cwd: Path) -> list[str]:
    output = git(["diff", "--name-only", f"{base}...{head}"], cwd)
    return [line.strip() for line in output.splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Require README updates when source files change.")
    parser.add_argument("--base", help="Base git ref/SHA. Defaults to origin/main or main.")
    parser.add_argument("--head", default="HEAD", help="Head git ref/SHA.")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    base = args.base
    if not base:
        for candidate in ("origin/main", "main"):
            try:
                git(["rev-parse", "--verify", candidate], repo)
                base = candidate
                break
            except RuntimeError:
                continue
    if not base:
        print("README check skipped: no base ref found.")
        return 0

    files = changed_files(base, args.head, repo)
    src_changed = any(path.startswith("src/") for path in files)
    if not src_changed:
        print("No src/ changes - README check skipped.")
        return 0

    readme_changed = any(path in README_FILES for path in files)
    if readme_changed:
        print("README updated - check passed.")
        return 0

    print("")
    print("README check failed: src/ changed but README.md or README_en.md was not updated.")
    print("Update the Chinese primary README.md and/or English README_en.md before pushing.")
    print("")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
