"""Tests for v0.6.1 Orchestrator runtime state."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import multi_agent_brief.orchestrator.runtime_state as runtime_state
from multi_agent_brief.cli.main import main
from multi_agent_brief.orchestrator.runtime_state import (
    RUNTIME_STATE_FILES,
    RuntimeStateError,
    check_runtime_state,
    initialize_runtime_state,
    record_decision,
    show_runtime_state,
)


ROOT = Path(__file__).resolve().parent.parent


def _write_workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "input").mkdir()
    (ws / "config.yaml").write_text(
        """
project:
  name: "Runtime State Test"
output:
  path: "output"
input:
  path: "input"
""".strip(),
        encoding="utf-8",
    )
    (ws / "user.md").write_text("# User\n", encoding="utf-8")
    (ws / "sources.yaml").write_text("manual:\n  sources: []\n", encoding="utf-8")
    return ws


def _state_file(ws: Path, key: str) -> Path:
    return ws / RUNTIME_STATE_FILES[key]


def test_state_init_creates_runtime_control_files_without_old_run_manifest(tmp_path):
    ws = _write_workspace(tmp_path)

    state = initialize_runtime_state(workspace=ws, repo_workdir=ROOT)

    assert state["ok"] is True
    assert _state_file(ws, "runtime_manifest").exists()
    assert _state_file(ws, "workflow_state").exists()
    assert _state_file(ws, "event_log").exists()
    assert not (ws / "output" / "intermediate" / "run_manifest.json").exists()

    manifest = json.loads(_state_file(ws, "runtime_manifest").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "multi-agent-brief-runtime-manifest/v1"
    assert manifest["workspace"] == "."
    assert manifest["runtime_state_files"] == RUNTIME_STATE_FILES
    assert manifest["stage_order"][0] == "doctor"


def test_state_check_fresh_workspace_is_not_globally_blocked(tmp_path):
    ws = _write_workspace(tmp_path)
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)

    state = check_runtime_state(workspace=ws, repo_workdir=ROOT)
    workflow = state["workflow_state"]
    registry = state["artifact_registry"]["artifacts"]

    assert workflow["blocked"] is False
    assert workflow["current_stage"] == "doctor"
    assert workflow["stage_statuses"]["doctor"]["status"] == "ready"
    assert workflow["stage_statuses"]["claim-ledger"]["status"] == "pending"
    assert registry["claim_ledger"]["status"] == "expected"
    assert registry["audited_brief"]["status"] == "expected"
    assert registry["reader_brief"]["status"] == "expected"


def test_state_check_strict_fresh_workspace_returns_zero(tmp_path):
    ws = _write_workspace(tmp_path)

    rc = main([
        "state",
        "check",
        "--workspace",
        str(ws),
        "--repo-workdir",
        str(ROOT),
        "--strict",
        "--json",
    ])

    assert rc == 0


def test_required_artifact_missing_blocks_consumer_after_producer_complete(tmp_path):
    ws = _write_workspace(tmp_path)
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)

    for stage in ("doctor", "source-discovery", "input-governance", "scout"):
        record_decision(
            workspace=ws,
            repo_workdir=ROOT,
            stage_id=stage,
            decision="continue",
            reason=f"{stage} complete",
        )

    state = check_runtime_state(workspace=ws, repo_workdir=ROOT)
    workflow = state["workflow_state"]
    registry = state["artifact_registry"]["artifacts"]

    assert registry["candidate_claims"]["status"] == "missing"
    assert workflow["current_stage"] == "screener"
    assert workflow["stage_statuses"]["screener"]["status"] == "blocked"
    assert "candidate_claims" in workflow["blocking_reason"]
    assert workflow["stage_statuses"]["claim-ledger"]["status"] == "pending"


def test_invalid_current_stage_output_blocks_only_that_stage(tmp_path):
    ws = _write_workspace(tmp_path)
    output = ws / "output" / "intermediate"
    output.mkdir(parents=True)
    (output / "candidate_claims.json").write_text("{broken", encoding="utf-8")
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)

    for stage in ("doctor", "source-discovery", "input-governance"):
        record_decision(
            workspace=ws,
            repo_workdir=ROOT,
            stage_id=stage,
            decision="continue",
            reason=f"{stage} complete",
        )

    state = check_runtime_state(workspace=ws, repo_workdir=ROOT)
    workflow = state["workflow_state"]
    registry = state["artifact_registry"]["artifacts"]

    assert registry["candidate_claims"]["status"] == "invalid"
    assert workflow["current_stage"] == "scout"
    assert workflow["stage_statuses"]["scout"]["status"] == "blocked"
    assert workflow["stage_statuses"]["claim-ledger"]["status"] == "pending"


def test_state_decide_validates_decision_vocabulary(tmp_path, capsys):
    ws = _write_workspace(tmp_path)
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)

    rc = main([
        "state",
        "decide",
        "--workspace",
        str(ws),
        "--repo-workdir",
        str(ROOT),
        "--stage",
        "doctor",
        "--decision",
        "invent_decision",
        "--reason",
        "bad",
        "--json",
    ])

    assert rc == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert "Unknown Orchestrator decision" in payload["error"]


def test_state_decide_records_event_and_last_decision(tmp_path):
    ws = _write_workspace(tmp_path)
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)

    state = record_decision(
        workspace=ws,
        repo_workdir=ROOT,
        stage_id="doctor",
        decision="continue",
        reason="doctor passed",
    )

    workflow = state["workflow_state"]
    assert workflow["last_decision"]["decision"] == "continue"
    assert workflow["stage_statuses"]["doctor"]["status"] == "complete"
    assert workflow["current_stage"] == "source-discovery"
    events = _state_file(ws, "event_log").read_text(encoding="utf-8").strip().splitlines()
    assert any(json.loads(line)["event_type"] == "decision_recorded" for line in events)


def test_state_decide_rejects_out_of_order_stage_and_leaves_workflow_unchanged(tmp_path, capsys):
    ws = _write_workspace(tmp_path)
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)
    before = json.loads(_state_file(ws, "workflow_state").read_text(encoding="utf-8"))

    rc = main([
        "state",
        "decide",
        "--workspace",
        str(ws),
        "--repo-workdir",
        str(ROOT),
        "--stage",
        "auditor",
        "--decision",
        "continue",
        "--reason",
        "out of order",
        "--json",
    ])

    assert rc == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert "does not match current stage" in payload["error"]
    after = json.loads(_state_file(ws, "workflow_state").read_text(encoding="utf-8"))
    assert after == before


def test_state_decide_event_failure_leaves_workflow_unchanged(tmp_path, monkeypatch):
    ws = _write_workspace(tmp_path)
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)
    before = json.loads(_state_file(ws, "workflow_state").read_text(encoding="utf-8"))

    def fail_append(*args, **kwargs):
        raise RuntimeStateError("event append failed")

    monkeypatch.setattr(runtime_state, "_append_jsonl", fail_append)

    with pytest.raises(RuntimeStateError):
        record_decision(
            workspace=ws,
            repo_workdir=ROOT,
            stage_id="doctor",
            decision="continue",
            reason="doctor passed",
        )

    after = json.loads(_state_file(ws, "workflow_state").read_text(encoding="utf-8"))
    assert after == before


def test_state_check_preserves_explicit_block_decision(tmp_path):
    ws = _write_workspace(tmp_path)
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)
    record_decision(
        workspace=ws,
        repo_workdir=ROOT,
        stage_id="doctor",
        decision="block_run",
        reason="doctor failed",
    )

    state = check_runtime_state(workspace=ws, repo_workdir=ROOT)

    assert state["workflow_state"]["blocked"] is True
    assert state["workflow_state"]["current_stage"] == "doctor"
    assert state["workflow_state"]["stage_statuses"]["doctor"]["status"] == "blocked"
    assert state["workflow_state"]["blocking_reason"] == "doctor failed"


def test_state_check_event_failure_leaves_state_unchanged(tmp_path, monkeypatch):
    ws = _write_workspace(tmp_path)
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)
    for stage in ("doctor", "source-discovery", "input-governance", "scout"):
        record_decision(
            workspace=ws,
            repo_workdir=ROOT,
            stage_id=stage,
            decision="continue",
            reason=f"{stage} complete",
        )
    before = json.loads(_state_file(ws, "workflow_state").read_text(encoding="utf-8"))

    def fail_append(*args, **kwargs):
        raise RuntimeStateError("event append failed")

    monkeypatch.setattr(runtime_state, "_append_jsonl", fail_append)

    with pytest.raises(RuntimeStateError):
        check_runtime_state(workspace=ws, repo_workdir=ROOT)

    after = json.loads(_state_file(ws, "workflow_state").read_text(encoding="utf-8"))
    assert after == before
    assert not _state_file(ws, "artifact_registry").exists()


def test_state_check_only_writes_changed_events_once(tmp_path):
    ws = _write_workspace(tmp_path)
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)
    for stage in ("doctor", "source-discovery", "input-governance", "scout"):
        record_decision(
            workspace=ws,
            repo_workdir=ROOT,
            stage_id=stage,
            decision="continue",
            reason=f"{stage} complete",
        )

    check_runtime_state(workspace=ws, repo_workdir=ROOT)
    first_events = _state_file(ws, "event_log").read_text(encoding="utf-8").strip().splitlines()
    check_runtime_state(workspace=ws, repo_workdir=ROOT)
    second_events = _state_file(ws, "event_log").read_text(encoding="utf-8").strip().splitlines()

    assert len(second_events) == len(first_events)
    event_types = [json.loads(line)["event_type"] for line in first_events]
    assert event_types.count("stage_status_changed") == 1
    assert event_types.count("run_blocked") == 1


def test_state_show_json_handles_corrupted_state_without_traceback(tmp_path, capsys):
    ws = _write_workspace(tmp_path)
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)
    _state_file(ws, "workflow_state").write_text("{broken", encoding="utf-8")

    rc = main(["state", "show", "--workspace", str(ws), "--json"])

    assert rc == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert "Invalid JSON state file" in payload["error"]


def test_reset_state_archives_old_event_log(tmp_path):
    ws = _write_workspace(tmp_path)
    first = initialize_runtime_state(workspace=ws, repo_workdir=ROOT)
    old_run_id = first["manifest"]["run_id"]

    second = initialize_runtime_state(
        workspace=ws,
        repo_workdir=ROOT,
        reset_state=True,
    )

    assert second["manifest"]["run_id"] != old_run_id
    archived = ws / "output" / "intermediate" / f"event_log.{old_run_id}.jsonl"
    assert archived.exists()
    assert _state_file(ws, "event_log").exists()
    reset_event = json.loads(_state_file(ws, "event_log").read_text(encoding="utf-8").splitlines()[0])
    assert reset_event["event_type"] == "run_reset"
    assert reset_event["metadata"]["previous_run_id"] == old_run_id
    assert reset_event["metadata"]["archived_event_log"] == f"output/intermediate/event_log.{old_run_id}.jsonl"


def test_reset_state_recovers_from_corrupted_workflow_state(tmp_path):
    ws = _write_workspace(tmp_path)
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)
    _state_file(ws, "workflow_state").write_text("{broken", encoding="utf-8")

    state = initialize_runtime_state(
        workspace=ws,
        repo_workdir=ROOT,
        reset_state=True,
    )

    assert state["ok"] is True
    assert state["workflow_state"]["current_stage"] == "doctor"


def test_state_paths_are_workspace_relative(tmp_path):
    ws = _write_workspace(tmp_path)
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)
    state = check_runtime_state(workspace=ws, repo_workdir=ROOT)

    assert state["manifest"]["runtime_state_files"] == RUNTIME_STATE_FILES
    for record in state["artifact_registry"]["artifacts"].values():
        assert not Path(record["path"]).is_absolute()


def test_show_runtime_state_reports_event_count(tmp_path):
    ws = _write_workspace(tmp_path)
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)

    state = show_runtime_state(workspace=ws)

    assert state["event_count"] >= 1
