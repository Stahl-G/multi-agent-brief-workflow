"""Runtime validation for durable source evidence pack manifests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

SOURCE_EVIDENCE_PACK_VALIDATION_PREFIX = "source_evidence_pack_manifest_validation_error"


def validate_source_evidence_pack_manifest(
    *,
    manifest_payload: Mapping[str, Any],
    workspace: Path,
) -> str | None:
    records = manifest_payload.get("records")
    if not isinstance(records, list) or not records:
        return "records_missing"

    seen_paths: set[str] = set()
    normalized_records: list[dict[str, Any]] = []
    for idx, record in enumerate(records):
        if not isinstance(record, dict):
            return f"record_invalid:{idx}"
        source_id = _text(record.get("source_id"))
        if not source_id:
            return f"source_id_missing:{idx}"
        path_text = _text(record.get("path"))
        if not path_text:
            return f"path_missing:{source_id}"
        if path_text in seen_paths:
            return f"duplicate_path:{path_text}"
        seen_paths.add(path_text)

        path, reason = _resolve_source_pack_path(
            workspace=workspace,
            path_text=path_text,
            source_id=source_id,
        )
        if reason:
            return reason
        assert path is not None
        if not path.exists() or not path.is_file():
            return f"source_file_missing:{source_id}"

        expected_sha = _text(record.get("sha256"))
        if not _valid_sha(expected_sha):
            return f"source_sha_invalid:{source_id}"
        actual_sha = _sha256_file(path)
        if actual_sha != expected_sha:
            return f"source_sha_mismatch:{source_id}"

        expected_size = record.get("size_bytes")
        if type(expected_size) is not int or expected_size <= 0:
            return f"source_size_invalid:{source_id}"
        actual_size = path.stat().st_size
        if actual_size != expected_size:
            return f"source_size_mismatch:{source_id}"

        normalized_records.append({
            "path": path_text,
            "sha256": expected_sha,
            "size_bytes": expected_size,
            "source_id": source_id,
        })

    expected_pack_sha = _text(manifest_payload.get("pack_sha256"))
    if not _valid_sha(expected_pack_sha):
        return "pack_sha_invalid"
    actual_pack_sha = _sha256_json(normalized_records)
    if actual_pack_sha != expected_pack_sha:
        return "pack_sha_mismatch"
    return None


def _resolve_source_pack_path(
    *,
    workspace: Path,
    path_text: str,
    source_id: str,
) -> tuple[Path | None, str | None]:
    if "\\" in path_text:
        return None, f"path_unsafe:{source_id}"
    posix = PurePosixPath(path_text)
    if posix.is_absolute() or ".." in posix.parts:
        return None, f"path_unsafe:{source_id}"
    if posix.parts[:2] != ("input", "sources"):
        return None, f"path_unsafe:{source_id}"

    ws = workspace.expanduser().resolve()
    input_root_unresolved = ws / "input"
    source_root_unresolved = ws / "input" / "sources"
    if (
        (input_root_unresolved.exists() and input_root_unresolved.is_symlink())
        or (source_root_unresolved.exists() and source_root_unresolved.is_symlink())
    ):
        return None, f"path_unsafe:{source_id}"
    resolved = (ws / Path(*posix.parts)).resolve()
    source_root = source_root_unresolved.resolve()
    try:
        resolved.relative_to(source_root)
    except ValueError:
        return None, f"path_unsafe:{source_id}"
    return resolved, None


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_json(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _valid_sha(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
