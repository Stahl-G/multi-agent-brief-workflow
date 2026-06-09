"""Provenance control artifact contract helpers."""

from __future__ import annotations

from pathlib import Path

from multi_agent_brief.provenance.model import PROVENANCE_GRAPH_FILE


PROVENANCE_STATE_FILES = {"provenance_graph": PROVENANCE_GRAPH_FILE}


def provenance_paths(workspace: str | Path) -> dict[str, Path]:
    ws = Path(workspace).expanduser().resolve()
    return {key: ws / rel_path for key, rel_path in PROVENANCE_STATE_FILES.items()}


def provenance_artifact_activated(*, workspace: str | Path, artifact_id: str) -> bool:
    if artifact_id != "provenance_graph":
        return False
    return provenance_paths(workspace)["provenance_graph"].exists()
