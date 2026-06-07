"""inputs — workspace input classification and governance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Classification constants
# ---------------------------------------------------------------------------

# Known input subdirectory → classification role
DIR_ROLES: dict[str, str] = {
    "sources": "evidence",
    "feedback": "feedback",
    "instructions": "instruction",
    "context": "context",
}

# Non-evidence input subdirectories that ManualProvider must block
NON_EVIDENCE_SUBDIRS = {"feedback", "instructions", "context"}

# Recognised text-file extensions for evidence content
RECOGNISED_EVIDENCE_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".csv"}

# All content files we attempt to classify (including non-text for skipped records)
SCANNABLE_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".csv", ".pdf", ".docx", ".xlsx"}

# ---------------------------------------------------------------------------
# Artifact hygiene — file names / patterns that signal old output artefacts
# ---------------------------------------------------------------------------

SUSPICIOUS_FILENAMES: set[str] = {
    "brief.md", "audited_brief.md", "reader_brief.md",
    "audit_report.json", "finalize_report.json",
    "claim_ledger.json", "candidate_claims.json", "screened_candidates.json",
    "input_classification.json", "classification.json",
    "run_manifest.json", "source_map.md", "source_coverage_report.json",
    "analysis_blocks.json", "rendered_output_report.json",
    "final_audit_report.json", "final_clean_report.json", "editor_draft.md",
    "analyst_draft.md", "draft_brief.md",
}

SUSPICIOUS_SUFFIX_PATTERNS: tuple[str, ...] = (
    "_output.md", "_final.md", "_audit.md", "_audited.md",
    "_reviewed.md", "_commented.md",
)

SUSPICIOUS_CONTENT_MARKERS: tuple[str, ...] = (
    "[src:", "audit_status", "claim_id", "CLAIM_ID",
    "Reader brief", "Internal [src:", "Finalized report",
    "Audit report", "Evidence ledger",
)

# ---------------------------------------------------------------------------
# Feedback / instruction / context detection by filename keyword
# ---------------------------------------------------------------------------

FEEDBACK_KEYWORDS: tuple[str, ...] = (
    "feedback", "comment", "comments", "annotated",
    "review", "revision",
    "批注", "修改意见", "反馈",
)

INSTRUCTION_KEYWORDS: tuple[str, ...] = (
    "instruction", "instructions", "prompt",
    "requirements", "briefing_request",
    "任务要求", "写作要求",
)

CONTEXT_KEYWORDS: tuple[str, ...] = (
    "context", "background", "company_profile", "profile",
    "背景", "公司介绍",
)


# ---------------------------------------------------------------------------
# CLI registration
# ---------------------------------------------------------------------------

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
        help="Output JSON path (default: <output.path>/input_classification.json).",
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


# ---------------------------------------------------------------------------
# Classify command
# ---------------------------------------------------------------------------

def _handle_classify(args: argparse.Namespace) -> int:
    """Classify input/ files by role."""
    config_path = Path(args.config).resolve()
    if not config_path.exists():
        print(f"[inputs] config.yaml not found: {config_path}", flush=True)
        return 1

    workspace = config_path.parent

    # ── load config to read input.path / output.path ──
    from multi_agent_brief.core.config import load_config
    try:
        cfg = load_config(config_path)
    except Exception as exc:
        print(f"[inputs] Failed to read config: {exc}", flush=True)
        return 1

    input_cfg = cfg.get("input", {}) or {}
    output_cfg = cfg.get("output", {}) or {}

    raw_input_path = input_cfg.get("path", "input")
    input_path = Path(raw_input_path)
    if not input_path.is_absolute():
        input_path = workspace / input_path

    if not input_path.is_dir():
        print(f"[inputs] No input directory found: {input_path}", flush=True)
        return 1

    classified = _classify_input_dir(input_path)

    # ── resolve output path ──
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        raw_output_path = output_cfg.get("path", "output")
        output_dir = Path(raw_output_path)
        if not output_dir.is_absolute():
            output_dir = workspace / output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "input_classification.json"

    payload = json.dumps(classified, ensure_ascii=False, indent=2)
    output_path.write_text(payload, encoding="utf-8")

    if not args.quiet:
        _print_summary(classified)

    print(f"[inputs] Classification written: {output_path}", flush=True)
    return 0


# ---------------------------------------------------------------------------
# Core classification logic
# ---------------------------------------------------------------------------

def _classify_input_dir(input_dir: Path) -> dict[str, Any]:
    """Scan input_dir and classify every content file.

    Returns a dict with keys:
      "evidence", "feedback", "instruction", "context", "skipped"
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
            role = DIR_ROLES.get(entry.name)
            if role is None:
                # Unknown directory — record all files inside as skipped
                for item in _scan_dir_entries(entry):
                    item["reason"] = "unknown_input_subdir"
                    item["suggested_role"] = "unknown"
                    skipped.append(item)
                continue

            for item in _scan_dir_entries(entry):
                _assign_by_role(role, item, evidence, feedback, instruction, context, skipped)

        elif entry.is_file():
            # Root-level files — backward-compatible, but run hygiene check
            _classify_root_file(entry, evidence, skipped)

    return {
        "evidence": evidence,
        "feedback": feedback,
        "instruction": instruction,
        "context": context,
        "skipped": skipped,
    }


def _scan_dir_entries(subdir: Path) -> list[dict[str, Any]]:
    """Return metadata dicts for every scannable file one level deep under subdir."""
    items: list[dict[str, Any]] = []
    for f in sorted(subdir.iterdir()):
        if f.name.startswith(".") or f.name.lower() == "readme.md":
            continue
        if f.is_dir():
            # Nested directory — record as skipped
            items.append({
                "path": str(f),
                "name": f.name + "/",
                "bytes": 0,
                "reason": "nested_directory_not_supported",
            })
            continue
        try:
            size = f.stat().st_size
        except OSError:
            items.append({
                "path": str(f),
                "name": f.name,
                "bytes": 0,
                "reason": "unreadable",
            })
            continue
        items.append({"path": str(f), "name": f.name, "bytes": size})
    return items


def _classify_root_file(entry: Path, evidence: list, skipped: list) -> None:
    """Classify a file in the input/ root — legacy path with hygiene checks."""
    name_lower = entry.name.lower()

    # 1. Artifact hygiene — suspicious filename patterns
    if name_lower in SUSPICIOUS_FILENAMES:
        skipped.append(_skip_item(entry, "suspicious_output_artifact"))
        return

    for pattern in SUSPICIOUS_SUFFIX_PATTERNS:
        if name_lower.endswith(pattern):
            skipped.append(_skip_item(entry, "suspicious_output_artifact"))
            return

    # 2. Check for keyword-based role override
    override_role = _keyword_role(entry.name)
    if override_role in ("feedback", "instruction", "context"):
        skipped.append(_skip_item(entry, f"filename_suggests_{override_role}",
                                  suggested_role=override_role))
        return

    # 3. Check extension support
    if entry.suffix.lower() not in RECOGNISED_EVIDENCE_SUFFIXES:
        skipped.append(_skip_item(entry, "unsupported_extension"))
        return

    # 4. Check content for suspicious markers
    try:
        content = entry.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        skipped.append(_skip_item(entry, "binary_or_unreadable"))
        return

    if _has_suspicious_content(content):
        evidence.append(_content_item(entry, flagged=True))
        # Also note it in skipped as a warning-level finding
        skipped.append({
            **_base_item(entry),
            "reason": "suspicious_content_markers",
            "note": "File classified as evidence but contains markers of old output artefacts; review manually.",
        })
        return

    # 5. Clean — pass as evidence
    evidence.append(_content_item(entry))


def _assign_by_role(role: str, item: dict, evidence: list, feedback: list,
                    instruction: list, context: list, skipped: list) -> None:
    """Route an item from a known subdirectory to the right list."""
    # If item already has a `reason` (from _scan_dir_entries), it goes to skipped
    if "reason" in item:
        skipped.append(item)
        return

    # Check extension for content files
    ext = Path(item["name"]).suffix.lower()
    if ext not in SCANNABLE_SUFFIXES:
        item["reason"] = "unsupported_extension"
        item["suggested_role"] = role
        skipped.append(item)
        return

    if ext not in RECOGNISED_EVIDENCE_SUFFIXES:
        item["reason"] = "unsupported_extension"
        item["suggested_role"] = role
        skipped.append(item)
        return

    # Artifact-hygiene name check even within subdirs
    name_lower = item["name"].lower()
    if name_lower in SUSPICIOUS_FILENAMES:
        item["reason"] = "suspicious_output_artifact"
        item["suggested_role"] = role
        skipped.append(item)
        return

    # Content check (only for non-evidence roles — evidence files skip this
    # since suspicious content detection in subdirs is less reliable)
    if role != "evidence":
        try:
            content = Path(item["path"]).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            item["reason"] = "binary_or_unreadable"
            item["suggested_role"] = role
            skipped.append(item)
            return

        if _has_suspicious_content(content):
            item["reason"] = "suspicious_content_markers"
            item["suggested_role"] = role
            skipped.append(item)
            return

    # Route to final list
    target = {"evidence": evidence, "feedback": feedback,
              "instruction": instruction, "context": context}.get(role)
    if target is not None:
        target.append(item)


def _base_item(entry: Path) -> dict[str, Any]:
    try:
        size = entry.stat().st_size
    except OSError:
        size = 0
    return {"path": str(entry), "name": entry.name, "bytes": size}


def _content_item(entry: Path, flagged: bool = False) -> dict[str, Any]:
    item = _base_item(entry)
    if flagged:
        item["flagged"] = True
    return item


def _skip_item(entry: Path, reason: str, suggested_role: str = "") -> dict[str, Any]:
    item = _base_item(entry)
    item["reason"] = reason
    if suggested_role:
        item["suggested_role"] = suggested_role
    return item


def _keyword_role(filename: str) -> str | None:
    """Detect role from filename keywords."""
    name_lower = filename.lower()
    for kw in FEEDBACK_KEYWORDS:
        if kw in name_lower:
            return "feedback"
    for kw in INSTRUCTION_KEYWORDS:
        if kw in name_lower:
            return "instruction"
    for kw in CONTEXT_KEYWORDS:
        if kw in name_lower:
            return "context"
    return None


def _has_suspicious_content(content: str) -> bool:
    """Check if content contains markers suggesting it's an old output artifact."""
    if not content:
        return False
    # Quick scan — first 2000 chars are usually enough
    head = content[:2000].lower() if len(content) > 2000 else content.lower()
    for marker in SUSPICIOUS_CONTENT_MARKERS:
        if marker.lower() in head:
            return True
    return False


# ---------------------------------------------------------------------------
# Summary output
# ---------------------------------------------------------------------------

def _print_summary(classified: dict[str, Any]) -> None:
    """Print a human-readable summary."""
    print()
    print("=== Input Classification Summary ===")
    for role, label in [
        ("evidence", "📄 Evidence (claims-eligible)"),
        ("feedback", "✏️  Feedback (editorial direction)"),
        ("instruction", "📋 Instructions (task guidance)"),
        ("context", "📎 Context (background reference)"),
    ]:
        files = classified.get(role, [])
        count = len(files)
        print(f"  {label}: {count} file(s)")
        for f in files:
            note = ""
            if f.get("flagged"):
                note = " ⚠️ (suspicious content markers)"
            print(f"    - {f['name']}{note}")

    skipped_files = classified.get("skipped", [])
    skipped_count = len(skipped_files)
    print(f"  ⏭️  Skipped: {skipped_count} file(s)")
    if skipped_count > 0:
        for f in skipped_files:
            reason = f.get("reason", "unknown")
            suggested = f" → {f['suggested_role']}" if f.get("suggested_role") else ""
            print(f"    - {f['name']}  ({reason}{suggested})")
    print()
