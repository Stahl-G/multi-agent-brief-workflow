"""I/O helpers for provenance projection."""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from multi_agent_brief.provenance.model import ProvenanceError


def path_is_absolute_any_platform(value: str) -> bool:
    return (
        Path(value).is_absolute()
        or PurePosixPath(value).is_absolute()
        or PureWindowsPath(value).is_absolute()
    )


def path_has_traversal_any_platform(value: str) -> bool:
    return (
        ".." in Path(value).parts
        or ".." in PurePosixPath(value).parts
        or ".." in PureWindowsPath(value).parts
    )


def ensure_safe_relative_path(value: str, *, label: str = "path") -> None:
    if not value or value == ".":
        return
    if value.lower().startswith("file://"):
        raise ProvenanceError(f"{label} must not be a file:// path.", details={label: value})
    if path_is_absolute_any_platform(value):
        raise ProvenanceError(f"{label} must be relative, not absolute.", details={label: value})
    if path_has_traversal_any_platform(value):
        raise ProvenanceError(f"{label} must not contain path traversal.", details={label: value})


def workspace_relative(workspace: Path, path: Path) -> str:
    resolved_workspace = workspace.expanduser().resolve()
    resolved = path.expanduser().resolve()
    try:
        rel = resolved.relative_to(resolved_workspace).as_posix()
    except ValueError as exc:
        raise ProvenanceError(
            "Provenance path resolves outside workspace.",
            details={"workspace": str(resolved_workspace), "path": str(resolved)},
        ) from exc
    ensure_safe_relative_path(rel, label="path")
    return rel


def read_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProvenanceError(
            f"Invalid JSON {label}: {path}",
            details={"path": str(path), "reason": str(exc)},
        ) from exc
    except OSError as exc:
        raise ProvenanceError(
            f"Failed to read {label}: {path}",
            details={"path": str(path), "reason": str(exc)},
        ) from exc
    if not isinstance(data, dict):
        raise ProvenanceError(
            f"{label} must contain a JSON object: {path}",
            details={"path": str(path)},
        )
    return data


def read_json_object_if_exists(path: Path, *, label: str) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return read_json_object(path, label=label)


def read_jsonl(path: Path, *, label: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ProvenanceError(
            f"Failed to read {label}: {path}",
            details={"path": str(path), "reason": str(exc)},
        ) from exc
    for idx, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ProvenanceError(
                f"Invalid JSONL {label}: {path}:{idx}",
                details={"path": str(path), "line": idx, "reason": str(exc)},
            ) from exc
        if not isinstance(item, dict):
            raise ProvenanceError(
                f"{label} JSONL records must be objects: {path}:{idx}",
                details={"path": str(path), "line": idx},
            )
        records.append(item)
    return records


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    except OSError as exc:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        raise ProvenanceError(
            f"Failed to write provenance graph: {path}",
            details={"path": str(path), "reason": str(exc)},
        ) from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ProvenanceError(
            f"Failed to hash file: {path}",
            details={"path": str(path), "reason": str(exc)},
        ) from exc
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
