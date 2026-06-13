"""Repair routing CLI commands."""

from __future__ import annotations

import argparse
import json
from typing import Any

from multi_agent_brief.repair.router import route_repair


def register(subparsers: argparse._SubParsersAction) -> None:
    repair_parser = subparsers.add_parser(
        "repair",
        help="Route deterministic repair ownership without executing repair.",
    )
    actions = repair_parser.add_subparsers(dest="repair_action", required=True)
    route_parser = actions.add_parser(
        "route",
        help="Show allowed repair owner/artifacts for the current workspace issue.",
    )
    route_parser.add_argument("--workspace", required=True, help="Path to workspace directory.")
    route_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")


def handle(args: argparse.Namespace) -> int:
    if args.repair_action != "route":
        return 1
    payload = route_repair(workspace=args.workspace)
    if getattr(args, "json", False):
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        _print_route(payload)
    return 0 if payload.get("ok") else 1


def _print_route(payload: dict[str, Any]) -> None:
    if not payload.get("ok"):
        print(f"[repair route] Error: {payload.get('message') or payload.get('error')}")
        return
    print(f"[repair route] owner: {payload.get('repair_owner')}")
    print(f"[repair route] must_rerun_from: {payload.get('must_rerun_from') or 'none'}")
    print(f"[repair route] reason: {payload.get('reason')}")
    print("[repair route] allowed_artifacts:")
    for artifact in payload.get("allowed_artifacts") or []:
        print(f"  - {artifact}")
    blocked = payload.get("blocked_direct_edits") or []
    if blocked:
        print("[repair route] blocked_direct_edits:")
        for artifact in blocked:
            print(f"  - {artifact}")
