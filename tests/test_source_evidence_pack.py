"""Tests for durable source evidence pack materialization."""

from __future__ import annotations

import json
from pathlib import Path

from multi_agent_brief.cli.main import main
from multi_agent_brief.orchestrator.runtime_state.operations import (
    check_runtime_state,
    initialize_runtime_state,
)

ROOT = Path(__file__).resolve().parent.parent


def _workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "input" / "raw").mkdir(parents=True)
    (ws / "config.yaml").write_text(
        "project:\n  name: Source Evidence Pack Test\n"
        "output:\n  path: output\n"
        "input:\n  path: input\n",
        encoding="utf-8",
    )
    (ws / "user.md").write_text("# User\n", encoding="utf-8")
    return ws


def test_sources_materialize_pack_writes_durable_source_records_and_manifest(
    tmp_path: Path,
    capsys,
) -> None:
    ws = _workspace(tmp_path)
    source = ws / "input" / "raw" / "source-001.md"
    source.write_text("# Source 001\n\nDurable evidence text.\n", encoding="utf-8")
    (ws / "sources.yaml").write_text(
        "source_strategy:\n"
        "  enabled_providers:\n"
        "    - manual\n"
        "manual:\n"
        "  sources:\n"
        "    - name: Regulator Bulletin\n"
        "      path: input/raw/source-001.md\n"
        "      category: regulator_record\n"
        "      reliability: high\n",
        encoding="utf-8",
    )
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)

    assert main([
        "sources",
        "materialize-pack",
        "--config",
        str(ws / "config.yaml"),
        "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["ok"] is True
    assert payload["record_count"] == 1
    assert payload["manifest_path"] == "output/intermediate/source_evidence_pack_manifest.json"
    record = payload["records"][0]
    assert record["path"].startswith("input/sources/")
    record_path = ws / record["path"]
    manifest_path = ws / payload["manifest_path"]
    assert record_path.exists()
    assert manifest_path.exists()

    record_payload = json.loads(record_path.read_text(encoding="utf-8"))
    assert record_payload["schema_version"] == "mabw.source_evidence_record.v1"
    assert record_payload["source_id"] == "SOURCE_001"
    assert record_payload["source_title"] == "Source 001"
    assert record_payload["publisher_or_institution"] == "Regulator Bulletin"
    assert record_payload["retrieval_source_type"] == "local_file"
    assert record_payload["underlying_evidence_type"] == "regulator_record"
    assert "Durable evidence text." in record_payload["content"]
    assert "semantic_support_assessment" in json.loads(
        manifest_path.read_text(encoding="utf-8")
    )["non_goals"]

    state = check_runtime_state(workspace=ws, repo_workdir=ROOT)
    registry_record = state["artifact_registry"]["artifacts"]["source_evidence_pack_manifest"]
    assert registry_record["status"] == "valid"
    assert registry_record["required"] is False
    assert registry_record["validation_result"] == "experimental_source_evidence_pack_manifest"


def test_sources_materialize_pack_refuses_search_only_sources(
    tmp_path: Path,
    capsys,
) -> None:
    ws = _workspace(tmp_path)
    (ws / "sources.yaml").write_text(
        "source_strategy:\n"
        "  enabled_providers:\n"
        "    - web_search\n"
        "web_search:\n"
        "  enabled: true\n"
        "  mode: runtime_tool\n",
        encoding="utf-8",
    )

    assert main([
        "sources",
        "materialize-pack",
        "--config",
        str(ws / "config.yaml"),
        "--json",
    ]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["ok"] is False
    assert "manual or cached_package" in payload["error"]
    assert not (ws / "input" / "sources").exists()
    assert not (ws / "output" / "intermediate" / "source_evidence_pack_manifest.json").exists()


def test_source_evidence_pack_manifest_invalid_when_source_record_changes(
    tmp_path: Path,
    capsys,
) -> None:
    ws = _workspace(tmp_path)
    source = ws / "input" / "raw" / "source-001.md"
    source.write_text("# Source 001\n\nDurable evidence text.\n", encoding="utf-8")
    (ws / "sources.yaml").write_text(
        "source_strategy:\n"
        "  enabled_providers:\n"
        "    - manual\n"
        "manual:\n"
        "  sources:\n"
        "    - name: Regulator Bulletin\n"
        "      path: input/raw/source-001.md\n",
        encoding="utf-8",
    )
    initialize_runtime_state(workspace=ws, repo_workdir=ROOT)
    assert main([
        "sources",
        "materialize-pack",
        "--config",
        str(ws / "config.yaml"),
        "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)
    record_path = ws / payload["records"][0]["path"]
    record_path.write_text(record_path.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")

    state = check_runtime_state(workspace=ws, repo_workdir=ROOT)
    registry_record = state["artifact_registry"]["artifacts"]["source_evidence_pack_manifest"]
    assert registry_record["status"] == "invalid"
    assert (
        registry_record["validation_result"]
        == "source_evidence_pack_manifest_validation_error:source_sha_mismatch:SOURCE_001"
    )
