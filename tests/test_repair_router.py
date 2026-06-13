from __future__ import annotations

import json
from pathlib import Path

from multi_agent_brief.cli.main import main
from multi_agent_brief.orchestrator.runtime_state import initialize_runtime_state, runtime_state_paths


def _workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "config.yaml").write_text("project:\n  name: repair-route-test\n", encoding="utf-8")
    (ws / "sources.yaml").write_text("manual:\n  sources: []\n", encoding="utf-8")
    (ws / "user.md").write_text("# Repair route test\n", encoding="utf-8")
    return ws


def _intermediate(ws: Path) -> Path:
    path = ws / "output" / "intermediate"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_audit_report(ws: Path, finding: dict[str, object]) -> None:
    (_intermediate(ws) / "audit_report.json").write_text(
        json.dumps(
            {
                "audit_status": "fail",
                "audit_score": 40,
                "findings": [finding],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _write_quality_gate_report(ws: Path, finding: dict[str, object]) -> None:
    path = _intermediate(ws) / "gates" / "auditor_quality_gate_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "multi-agent-brief-quality-gates/v1",
                "status": "fail",
                "findings": [finding],
                "metadata": {"gate_stage_id": "auditor"},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_repair_route_maps_unsupported_claim_to_audited_brief(tmp_path, capsys):
    ws = _workspace(tmp_path)
    initialize_runtime_state(workspace=ws)
    before_events = runtime_state_paths(ws)["event_log"].read_bytes()
    _write_audit_report(
        ws,
        {
            "finding_id": "AUDIT_001",
            "finding_type": "unsupported_claim",
            "severity": "high",
            "artifact_id": "audited_brief",
            "description": "Claim in audited brief is unsupported by the ledger.",
        },
    )

    rc = main(["repair", "route", "--workspace", str(ws), "--json"])

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["repair_owner"] == "analyst/editor"
    assert payload["allowed_artifacts"] == ["output/intermediate/audited_brief.md"]
    assert payload["must_rerun_from"] == "auditor"
    assert "output/intermediate/audit_report.json" in payload["blocked_direct_edits"]
    assert not (ws / "output" / "intermediate" / "repair_plan.json").exists()
    assert runtime_state_paths(ws)["event_log"].read_bytes() == before_events


def test_repair_route_maps_claim_ledger_invalid_registry_to_claim_ledger(tmp_path, capsys):
    ws = _workspace(tmp_path)
    initialize_runtime_state(workspace=ws)
    registry_path = runtime_state_paths(ws)["artifact_registry"]
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": "multi-agent-brief-artifact-registry/v1",
                "run_id": "run-test",
                "artifacts": {
                    "claim_ledger": {
                        "artifact_id": "claim_ledger",
                        "path": "output/intermediate/claim_ledger.json",
                        "status": "invalid",
                        "validation_result": "claim_ledger_schema_error:claim[0].evidence_text",
                        "blocking_reason": "Claim Ledger missing evidence_text.",
                    }
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    rc = main(["repair", "route", "--workspace", str(ws), "--json"])

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["repair_owner"] == "claim-ledger"
    assert payload["allowed_artifacts"] == ["output/intermediate/claim_ledger.json"]
    assert payload["must_rerun_from"] == "analyst"
    assert "output/intermediate/audited_brief.md" in payload["blocked_direct_edits"]


def test_repair_route_maps_missing_source_excerpt_to_source_discovery(tmp_path, capsys):
    ws = _workspace(tmp_path)
    initialize_runtime_state(workspace=ws)
    _write_quality_gate_report(
        ws,
        {
            "finding_id": "QG_SOURCE_001",
            "finding_type": "source_pack_missing_raw_excerpt",
            "severity": "high",
            "artifact_id": "candidate_claims",
            "message": "Source pack missing raw excerpt/snippet for cited item.",
        },
    )

    rc = main(["repair", "route", "--workspace", str(ws), "--json"])

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["repair_owner"] == "source-discovery"
    assert payload["allowed_artifacts"] == ["input/sources/*"]
    assert payload["must_rerun_from"] == "input-governance"
    assert "output/intermediate/claim_ledger.json" in payload["blocked_direct_edits"]


def test_repair_route_no_match_is_read_only_none_route(tmp_path, capsys):
    ws = _workspace(tmp_path)
    initialize_runtime_state(workspace=ws)

    rc = main(["repair", "route", "--workspace", str(ws), "--json"])

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["repair_owner"] == "none"
    assert payload["routes"] == []
    assert payload["reason"] == "No deterministic repair route found."
