from __future__ import annotations

import json
from pathlib import Path

import yaml

from multi_agent_brief.agents.scout import load_local_sources
from multi_agent_brief.audit.deterministic import parse_date
from multi_agent_brief.audit.final_quality import build_final_quality_config
from multi_agent_brief.core.config import build_run_settings
from multi_agent_brief.core.pipeline import BriefPipeline
from multi_agent_brief.core.schemas import PipelineContext
from multi_agent_brief.onboarding.io import load_onboarding_result
from multi_agent_brief.onboarding.mapper import map_onboarding_to_profile
from multi_agent_brief.sources.base import SourceConfig, SourceItem, SourceQuery
from multi_agent_brief.sources.decider import merge_candidates_to_sources
from multi_agent_brief.sources.normalizer import filter_by_recency
from multi_agent_brief.sources.registry import collect_all_sources, validate_all_providers


def test_manual_provider_invalid_json_object_does_not_drop_valid_files(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "news.md").write_text(
        "- Valid manufacturing source line with enough content for extraction.\n",
        encoding="utf-8",
    )
    (input_dir / "bad.json").write_text("[]", encoding="utf-8")
    config = SourceConfig(
        enabled_providers=["manual"],
        manual={"enabled": True, "sources": [{"name": "Local", "path": str(input_dir)}]},
    )

    items, errors = collect_all_sources(config, SourceQuery(recency_days=0))

    assert len(items) == 1
    assert items[0].title == "News"
    assert any(err["error_type"] == "invalid_json_structure" for err in errors)


def test_scout_fallback_invalid_json_object_is_diagnostic_not_crash(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "news.md").write_text("- Valid local reportable item with enough text.\n", encoding="utf-8")
    (input_dir / "bad.json").write_text("null", encoding="utf-8")

    sources = load_local_sources(input_dir)

    assert any(source.source_id == "NEWS" for source in sources)
    bad = next(source for source in sources if source.source_id == "BAD")
    assert bad.source_type == "local_file_error"
    assert bad.metadata["error_type"] == "invalid_json_structure"


def test_recency_filter_handles_aware_dates_and_excludes_stale_or_future():
    items = [
        SourceItem(
            source_id="OLD",
            source_name="Old",
            source_type="web_search",
            title="Old",
            content="old",
            published_at="2026-01-01T00:00:00Z",
        ),
        SourceItem(
            source_id="FUTURE",
            source_name="Future",
            source_type="web_search",
            title="Future",
            content="future",
            published_at="2026-06-10",
        ),
        SourceItem(
            source_id="RECENT",
            source_name="Recent",
            source_type="web_search",
            title="Recent",
            content="recent",
            published_at="2026-06-01T00:00:00Z",
        ),
    ]

    result = filter_by_recency(items, 14, report_date="2026-06-02")

    assert [item.source_id for item in result] == ["RECENT"]


def test_parse_date_yyyymmdd_is_explicitly_supported():
    assert parse_date("20260602").isoformat() == "2026-06-02"


def test_registry_recency_zero_preserves_old_sources(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "old.json").write_text(
        json.dumps({"published_at": "2020-01-01", "content": "Old but intentionally unfiltered source."}),
        encoding="utf-8",
    )
    config = SourceConfig(
        enabled_providers=["manual"],
        manual={"enabled": True, "sources": [{"name": "Local", "path": str(input_dir)}]},
    )
    query = SourceQuery(recency_days=0)
    query.metadata["report_date"] = "2026-06-02"

    items, errors = collect_all_sources(config, query)

    assert not errors
    assert len(items) == 1
    assert items[0].source_id == "OLD"


def test_provider_validation_uses_sources_yaml_directory(tmp_path):
    workspace = tmp_path / "workspace"
    input_dir = workspace / "input"
    input_dir.mkdir(parents=True)
    config = SourceConfig(
        enabled_providers=["manual"],
        manual={"enabled": True, "sources": [{"name": "Local", "path": "input"}]},
        config_dir=str(workspace),
    )

    assert validate_all_providers(config) == []


def test_cached_package_relative_paths_use_sources_yaml_directory(tmp_path):
    workspace = tmp_path / "workspace"
    cache = workspace / "cache"
    cache.mkdir(parents=True)
    (cache / "items.md").write_text("Cached package reportable update with enough text.", encoding="utf-8")
    config = SourceConfig(
        enabled_providers=["cached_package"],
        cached_package={"enabled": True, "paths": ["cache"], "formats": ["md"]},
        config_dir=str(workspace),
    )

    items, errors = collect_all_sources(config, SourceQuery(recency_days=0))

    assert not errors
    assert len(items) == 1
    assert items[0].source_type == "cached"


def test_empty_pipeline_fails_audit_without_explicit_quiet_week(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    context = PipelineContext(
        project_name="Empty",
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        report_date="2026-06-02",
    )

    BriefPipeline().run(context)

    assert context.report_state.audit_report is not None
    assert context.report_state.audit_report.audit_status == "fail"
    assert any(f.finding_type == "no_reportable_claims" for f in context.report_state.audit_report.findings)


def test_merge_candidates_overwrite_replaces_url_and_rss_sources_but_keeps_local_input(tmp_path):
    sources_path = tmp_path / "sources.yaml"
    candidates_path = tmp_path / "source_candidates.yaml"
    sources_path.write_text(
        yaml.safe_dump(
            {
                "source_strategy": {"profile": "research", "enabled_providers": ["manual", "rss"]},
                "manual": {
                    "enabled": True,
                    "sources": [
                        {"name": "Local Input", "path": "input", "category": "local_files", "enabled": True},
                        {"name": "Old URL", "url": "https://old.example.com", "enabled": True},
                    ],
                },
                "rss": {"enabled": True, "feeds": [{"name": "Old RSS", "url": "https://old.example.com/rss"}]},
            }
        ),
        encoding="utf-8",
    )
    candidates_path.write_text(
        yaml.safe_dump(
            {
                "metadata": {"status": "pending_review"},
                "recommended_sources": [
                    {"name": "New URL", "url": "https://new.example.com/article", "category": "industry_media"},
                    {"name": "New RSS", "url": "https://new.example.com/rss", "category": "rss_feed"},
                ],
            }
        ),
        encoding="utf-8",
    )

    merge_candidates_to_sources(sources_path, candidates_path, overwrite=True)
    merged = yaml.safe_load(sources_path.read_text(encoding="utf-8"))

    manual_sources = merged["manual"]["sources"]
    assert any(src.get("category") == "local_files" for src in manual_sources)
    assert {src.get("url") for src in manual_sources if src.get("url")} == {"https://new.example.com/article"}
    assert [feed["url"] for feed in merged["rss"]["feeds"]] == ["https://new.example.com/rss"]


def test_stub_providers_are_validation_errors():
    config = SourceConfig(
        enabled_providers=["api", "filings", "mcp", "cli"],
        api={"enabled": True, "providers": []},
        mcp={"enabled": True, "servers": [], "scrapers": []},
    )

    errors = validate_all_providers(config)

    assert any("News API provider" in error for error in errors)
    assert any("Filings provider" in error for error in errors)
    assert any("MCP source provider" in error for error in errors)
    assert any("CLI source provider" in error for error in errors)


def test_string_false_booleans_parse_as_false(tmp_path):
    settings = build_run_settings(
        config={
            "report": {"fail_on_stale_source": "false"},
            "input": {"path": str(tmp_path / "input")},
            "output": {"path": str(tmp_path / "output")},
        },
        input_dir=None,
        output_dir=None,
        name=None,
        language=None,
        audience=None,
    )
    assert settings["fail_on_stale_source"] is False

    context = PipelineContext("Test", "/tmp/in", "/tmp/out")
    context.metadata["final_quality"] = {
        "quiet_week": "false",
        "require_dates": "false",
        "allow_quiet_week_exception": "false",
    }
    config = build_final_quality_config(context)
    assert config.quiet_week is False
    assert config.require_dates is False
    assert config.allow_quiet_week_exception is False


def test_onboarding_loader_normalizes_string_lists_and_default_docx(tmp_path):
    path = tmp_path / "onboarding.json"
    path.write_text(
        json.dumps({"must_watch": "policy", "forbidden_sources": "reddit"}),
        encoding="utf-8",
    )

    result = load_onboarding_result(path)
    profile = map_onboarding_to_profile(result)

    assert result.must_watch == ["policy"]
    assert result.forbidden_sources == ["reddit"]
    assert "policy" in profile.focus_areas
    assert profile.forbidden_sources == ["reddit"]
    assert "docx" in profile.output_formats


def test_setup_prompts_use_interactive_init():
    scripts_dir = Path(__file__).parents[1] / "scripts"
    for script_name in ("setup.sh", "setup.ps1"):
        text = (scripts_dir / script_name).read_text(encoding="utf-8")
        assert "multi-agent-brief init my-workspace --language" not in text
        assert "multi-agent-brief init my-workspace" in text
