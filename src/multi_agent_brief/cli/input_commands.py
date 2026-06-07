"""inputs — workspace input classification and governance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


# Known non-evidence subdirectories under input/
NON_EVIDENCE_DIRS = {"feedback", "instructions", "context"}

# File extensions that classify recognises as content files
RECOGNISED_SUFFIXES = {".md", ".txt", ".json"}


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the inputs subcommand group."""
    inputs_parser = subparsers.add_parser(
        "inputs", help="Input file classification and governance."
    )
    inputs_sub = inputs_parser.add_subparsers(
        dest="inputs_action", required=True
    )

    classify_parser = inputs_sub.add_parser(
        "classify",
        help="Classify input/ files by role (evidence / feedback / instruction / context).",
    )
    classify_parser.add_argument(
        "--config", required=True, help="Path to workspace config.yaml."
    )
    classify_parser.add_argument(
        "--output",
        help="Output JSON path (default: <workspace>/output/intermediate/input_classification.json).",
    )
    classify_parser.add_argument(
        "--quiet", action="store_true", help="Suppress summary output."
    )


def handle(args: argparse.Namespace) -> int:
    """Dispatch inputs subcommands."""
    if args.inputs_action == "classify":
        return _handle_classify(args)
    print(f"[inputs] Unknown action: {args.inputs_action}", flush=True)
    return 1


def _handle_classify(args: argparse.Namespace) -> int:
    """Classify input/ files by role."""
    config_path = Path(args.config).resolve()
    if not config_path.exists():
        print(f"[inputs] config.yaml not found: {config_path}", flush=True)
        return 1

    workspace = config_path.parent
    input_dir = workspace / "input"

    if not input_dir.is_dir():
        print(f"[inputs] No input/ directory in workspace: {workspace}", flush=True)
        return 1

    classified = _classify_input_dir(input_dir)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = workspace / "output" / "intermediate"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "input_classification.json"

    payload = json.dumps(classified, ensure_ascii=False, indent=2)
    output_path.write_text(payload, encoding="utf-8")

    if not args.quiet:
        _print_summary(classified)

    print(f"[inputs] Classification written: {output_path}", flush=True)
    return 0


def _classify_input_dir(input_dir: Path) -> dict[str, Any]:
    """Scan input/ and classify every content file by its parent subdirectory.

    Returns a dict with keys "evidence", "feedback", "instruction", "context",
    each containing a list of {"path": str, "name": str, "bytes": int}.
    """
    evidence: list[dict[str, Any]] = []
    feedback: list[dict[str, Any]] = []
    instruction: list[dict[str, Any]] = []
    context: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for entry in sorted(input_dir.iterdir()):
        if entry.name.startswith("."):
            continue

        if entry.is_dir():
            role = _dir_role(entry.name)
            if role is None:
                # Unknown directory — skip
                continue
            # Scan immediate children of the subdirectory
            for f in sorted(entry.iterdir()):
                if f.is_dir() or f.name.startswith(".") or f.name.lower() == "readme.md":
                    continue
                if f.suffix.lower() not in RECOGNISED_SUFFIXES:
                    continue
                item = {
                    "path": str(f),
                    "name": f.name,
                    "bytes": f.stat().st_size,
                }
                if role == "evidence":
                    evidence.append(item)
                elif role == "feedback":
                    feedback.append(item)
                elif role == "instruction":
                    instruction.append(item)
                elif role == "context":
                    context.append(item)
        elif entry.is_file():
            # Root-level files in input/ — backward compatible, treat as evidence
            if entry.suffix.lower() not in RECOGNISED_SUFFIXES:
                continue
            item = {
                "path": str(entry),
                "name": entry.name,
                "bytes": entry.stat().st_size,
            }
            evidence.append(item)

    return {
        "evidence": evidence,
        "feedback": feedback,
        "instruction": instruction,
        "context": context,
        "skipped": skipped,
    }


def _dir_role(name: str) -> str | None:
    """Map a subdirectory name to its classification role."""
    if name == "sources":
        return "evidence"
    if name == "feedback":
        return "feedback"
    if name == "instructions":
        return "instruction"
    if name == "context":
        return "context"
    # hermes_cache is not classified here — it's handled by the Hermes runtime
    return None


def _print_summary(classified: dict[str, Any]) -> None:
    """Print a human-readable summary."""
    print()
    print("=== Input Classification Summary ===")
    for role, label in [("evidence", "📄 Evidence (claims-eligible)"),
                        ("feedback", "✏️  Feedback (editorial direction)"),
                        ("instruction", "📋 Instructions (task guidance)"),
                        ("context", "📎 Context (background reference)")]:
        files = classified.get(role, [])
        count = len(files)
        print(f"  {label}: {count} file(s)")
        if count > 0:
            for f in files:
                print(f"    - {f['name']}")
    print()
