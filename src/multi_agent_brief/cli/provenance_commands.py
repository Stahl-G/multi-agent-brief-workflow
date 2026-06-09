"""Provenance projection CLI commands."""

from __future__ import annotations

import argparse
import json
from typing import Any

from multi_agent_brief.orchestrator.runtime_state import RuntimeStateError
from multi_agent_brief.provenance.builder import (
    build_provenance_workspace,
    show_provenance_workspace,
    validate_provenance_workspace,
)
from multi_agent_brief.provenance.model import ProvenanceError


def register(subparsers: argparse._SubParsersAction) -> None:
    provenance_parser = subparsers.add_parser(
        "provenance",
        help="Build and inspect deterministic workspace provenance projections.",
    )
    actions = provenance_parser.add_subparsers(dest="provenance_action", required=True)

    build_parser = actions.add_parser(
        "build",
        help="Build output/intermediate/provenance_graph.json from existing control files.",
    )
    build_parser.add_argument("--workspace", required=True, help="Path to workspace directory.")
    build_parser.add_argument("--repo-workdir", help="Repository or packaged contract base.")
    build_parser.add_argument("--strict", action="store_true", help="Fail when provenance warnings exist.")
    build_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    show_parser = actions.add_parser(
        "show",
        help="Show provenance graph summary.",
    )
    show_parser.add_argument("--workspace", required=True, help="Path to workspace directory.")
    show_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    validate_parser = actions.add_parser(
        "validate",
        help="Validate output/intermediate/provenance_graph.json.",
    )
    validate_parser.add_argument("--workspace", required=True, help="Path to workspace directory.")
    validate_parser.add_argument("--strict", action="store_true", help="Fail when provenance warnings exist.")
    validate_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")


def handle(args: argparse.Namespace) -> int:
    try:
        if args.provenance_action == "build":
            state = build_provenance_workspace(
                workspace=args.workspace,
                repo_workdir=getattr(args, "repo_workdir", None),
                strict=getattr(args, "strict", False),
            )
            _print_state("provenance build", state, as_json=getattr(args, "json", False))
            return 0 if state.get("ok") else 1

        if args.provenance_action == "show":
            state = show_provenance_workspace(workspace=args.workspace)
            _print_state("provenance show", state, as_json=getattr(args, "json", False))
            return 0 if state.get("ok") else 1

        if args.provenance_action == "validate":
            state = validate_provenance_workspace(
                workspace=args.workspace,
                strict=getattr(args, "strict", False),
            )
            _print_state("provenance validate", state, as_json=getattr(args, "json", False))
            return 0 if state.get("ok") else 1
    except (ProvenanceError, RuntimeStateError) as exc:
        _print_error(exc, as_json=getattr(args, "json", False))
        return 1
    return 1


def _print_state(label: str, state: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True))
        return
    validation = state.get("validation") or {}
    summary = (state.get("provenance_graph") or {}).get("summary") or state.get("summary") or {}
    print(f"[{label}] ok: {state.get('ok')}")
    print(f"[{label}] graph: {state.get('provenance_graph_path')}")
    print(f"[{label}] nodes: {summary.get('node_count', validation.get('node_count', 0))}")
    print(f"[{label}] edges: {summary.get('edge_count', validation.get('edge_count', 0))}")
    print(f"[{label}] warnings: {summary.get('warning_count', validation.get('warning_count', 0))}")
    print(f"[{label}] errors: {summary.get('error_count', validation.get('error_count', 0))}")
    for error in validation.get("errors") or []:
        print(f"  - {error}")


def _print_error(exc: Exception, *, as_json: bool) -> None:
    payload = exc.to_dict() if hasattr(exc, "to_dict") else {"ok": False, "error": str(exc)}
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"[provenance] {exc}")
