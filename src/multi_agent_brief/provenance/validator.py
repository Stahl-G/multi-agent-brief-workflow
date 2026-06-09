"""Provenance graph validation."""

from __future__ import annotations

import json
from typing import Any

from multi_agent_brief.provenance.io import ensure_safe_relative_path
from multi_agent_brief.provenance.model import (
    EDGE_TYPES,
    NODE_TYPES,
    PROVENANCE_GRAPH_SCHEMA,
    SEMANTIC_EDGE_TYPES,
)


RAW_CONTENT_KEYS = {
    "evidence_text",
    "source_text",
    "raw_source_text",
    "raw_text",
    "prompt",
    "system_prompt",
    "developer_prompt",
    "feedback_excerpt",
}


def validate_graph_payload(payload: dict[str, Any], *, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings = list(payload.get("warnings") or [])
    if payload.get("schema_version") != PROVENANCE_GRAPH_SCHEMA:
        errors.append("provenance_graph.json has an unsupported schema_version.")

    nodes = payload.get("nodes")
    edges = payload.get("edges")
    if not isinstance(nodes, list):
        errors.append("provenance_graph.json nodes must be a list.")
        nodes = []
    if not isinstance(edges, list):
        errors.append("provenance_graph.json edges must be a list.")
        edges = []

    node_ids: set[str] = set()
    for idx, node in enumerate(nodes):
        prefix = f"nodes[{idx}]"
        if not isinstance(node, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        node_id = str(node.get("id") or "")
        if not node_id:
            errors.append(f"{prefix}.id is required.")
        elif node_id in node_ids:
            errors.append(f"{prefix}.id is duplicated: {node_id}.")
        node_ids.add(node_id)
        if node.get("type") not in NODE_TYPES:
            errors.append(f"{prefix}.type is unknown: {node.get('type')}.")
        _check_path_fields(node, prefix=prefix, errors=errors)

    for idx, edge in enumerate(edges):
        prefix = f"edges[{idx}]"
        if not isinstance(edge, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        edge_type = str(edge.get("type") or "")
        if edge_type in SEMANTIC_EDGE_TYPES:
            errors.append(f"{prefix}.type is semantic and not allowed in v0.6.5: {edge_type}.")
        elif edge_type not in EDGE_TYPES:
            errors.append(f"{prefix}.type is unknown: {edge_type}.")
        source = str(edge.get("from") or "")
        target = str(edge.get("to") or "")
        if source not in node_ids:
            errors.append(f"{prefix}.from references missing node: {source}.")
        if target not in node_ids:
            errors.append(f"{prefix}.to references missing node: {target}.")
        _check_path_fields(edge, prefix=prefix, errors=errors)

    source_files = payload.get("source_files") or []
    if not isinstance(source_files, list):
        errors.append("provenance_graph.json source_files must be a list.")
        source_files = []
    for idx, item in enumerate(source_files):
        prefix = f"source_files[{idx}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        path = item.get("path")
        if not isinstance(path, str) or not path:
            errors.append(f"{prefix}.path is required.")
            continue
        _check_safe_path(path, prefix=f"{prefix}.path", errors=errors)

    _check_raw_content_keys(payload, errors=errors)
    if strict and warnings:
        errors.append("strict mode does not allow provenance warnings.")
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "warning_count": len(warnings),
        "error_count": len(errors),
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


def _check_path_fields(item: dict[str, Any], *, prefix: str, errors: list[str]) -> None:
    for key in ("path", "ref"):
        value = item.get(key)
        if isinstance(value, str):
            _check_safe_path(value, prefix=f"{prefix}.{key}", errors=errors)


def _check_safe_path(value: str, *, prefix: str, errors: list[str]) -> None:
    try:
        ensure_safe_relative_path(value, label=prefix)
    except Exception as exc:
        errors.append(str(exc))


def _check_raw_content_keys(value: Any, *, errors: list[str], path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key) in RAW_CONTENT_KEYS:
                errors.append(f"{path}.{key} must not be stored in provenance graph.")
            _check_raw_content_keys(child, errors=errors, path=f"{path}.{key}")
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            _check_raw_content_keys(child, errors=errors, path=f"{path}[{idx}]")


def graph_contains_text(payload: dict[str, Any], text: str) -> bool:
    if not text:
        return False
    return text in json.dumps(payload, ensure_ascii=False, sort_keys=True)
