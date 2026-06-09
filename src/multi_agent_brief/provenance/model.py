"""Provenance projection model helpers."""

from __future__ import annotations

from typing import Any


PROVENANCE_GRAPH_SCHEMA = "multi-agent-brief-provenance-graph/v1"
PROVENANCE_GRAPH_FILE = "output/intermediate/provenance_graph.json"

NODE_TYPES = {
    "run",
    "stage",
    "artifact",
    "claim",
    "source",
    "event",
    "decision",
    "feedback_issue",
    "repair_plan",
    "gate_finding",
}

EDGE_TYPES = {
    "run_has_stage",
    "stage_produces_artifact",
    "artifact_consumed_by_stage",
    "claim_cites_source",
    "claim_recorded_in_artifact",
    "artifact_references_claim",
    "artifact_references_source",
    "artifact_derived_from",
    "event_observed_artifact",
    "event_validated_artifact",
    "decision_applies_to_stage",
    "feedback_targets_stage",
    "feedback_targets_artifact",
    "repair_plan_addresses_issue",
    "gate_finding_targets_stage",
    "gate_finding_targets_artifact",
}

SEMANTIC_EDGE_TYPES = {
    "source_supports_claim",
    "semantic_supports",
    "verified_by_source",
    "truth_validated_by",
}


class ProvenanceError(Exception):
    """Raised when provenance projection cannot be built or validated."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": False,
            "error": str(self),
            "details": self.details,
        }


def node_id(node_type: str, raw_id: str) -> str:
    return f"{node_type}:{raw_id}"


def edge_key(edge: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(edge.get("from") or ""),
        str(edge.get("to") or ""),
        str(edge.get("type") or ""),
        str(edge.get("method") or ""),
    )


class GraphAccumulator:
    """Small deterministic graph builder with node and edge de-duplication."""

    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
        self._edges: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    def add_node(self, node: dict[str, Any]) -> None:
        node_id_value = str(node.get("id") or "")
        if not node_id_value:
            return
        existing = self._nodes.get(node_id_value)
        if existing:
            merged = dict(existing)
            merged.update({key: value for key, value in node.items() if value is not None})
            self._nodes[node_id_value] = merged
            return
        self._nodes[node_id_value] = node

    def add_edge(self, edge: dict[str, Any]) -> None:
        if not edge.get("from") or not edge.get("to") or not edge.get("type"):
            return
        self._edges[edge_key(edge)] = edge

    def nodes(self) -> list[dict[str, Any]]:
        return [self._nodes[key] for key in sorted(self._nodes)]

    def edges(self) -> list[dict[str, Any]]:
        return [
            self._edges[key]
            for key in sorted(self._edges, key=lambda item: (item[2], item[0], item[1], item[3]))
        ]
