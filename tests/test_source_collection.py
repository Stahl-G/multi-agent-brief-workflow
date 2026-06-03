"""Tests for the three-layer Source Collection architecture."""
from __future__ import annotations

from pathlib import Path

import pytest

from multi_agent_brief.core.pipeline import BriefPipeline
from multi_agent_brief.core.schemas import PipelineContext
from multi_agent_brief.sources.base import SourceConfig, SourceItem, SourceQuery
from multi_agent_brief.sources.planner import SourcePlan, SearchTask, create_source_plan
from multi_agent_brief.sources.industry_packs import get_industry_pack, list_industries
from multi_agent_brief.sources.web_search import WebSearchProvider
from multi_agent_brief.sources.search_backends.mock import MockSearchBackend
from multi_agent_brief.sources.cached_package import CachedPackageProvider
from multi_agent_brief.sources.registry import collect_all_sources


# --- SourcePlanner ---

def test_create_source_plan_solar():
    plan = create_source_plan(industry="solar", report_date="2026-06-02", recency_days=7)
    assert plan.industry == "solar"
    assert len(plan.search_tasks) > 0
    assert len(plan.rss_feeds) > 0
    assert any("pv-tech.org" in str(task.source_domains) for task in plan.search_tasks)


def test_create_source_plan_unknown_industry():
    plan = create_source_plan(industry="unknown", report_date="2026-06-02")
    assert plan.industry == "unknown"
    assert len(plan.search_tasks) == 0


def test_create_source_plan_with_extra_keywords():
    plan = create_source_plan(industry="solar", extra_keywords=["bifacial module"])
    assert any("bifacial" in task.query for task in plan.search_tasks)


# --- Industry Packs ---

def test_list_industries():
    industries = list_industries()
    assert "solar" in industries
    assert "technology" in industries


def test_get_industry_pack():
    pack = get_industry_pack("solar")
    assert pack is not None
    assert "rss_feeds" in pack
    assert "search_tasks" in pack


def test_get_industry_pack_unknown():
    pack = get_industry_pack("nonexistent")
    assert pack is None


# --- WebSearchProvider ---

def test_web_search_mock_backend():
    backend = MockSearchBackend()
    assert backend.is_available()
    results = backend.search("solar", max_results=2)
    assert len(results) == 2
    assert results[0].title  # not empty


def test_web_search_provider_collects():
    provider = WebSearchProvider(backend=MockSearchBackend())
    config = {"enabled": True}
    items = provider.collect(SourceQuery(keywords=["solar"]), config)
    assert len(items) > 0
    assert all(item.source_type == "web_search" for item in items)


def test_web_search_domain_filtering():
    """Search tasks with domains should be passed to backend."""
    provider = WebSearchProvider(backend=MockSearchBackend())
    config = {
        "enabled": True,
        "search_tasks": [
            {"query": "solar prices", "domains": ["pv-tech.org"]},
        ],
    }
    items = provider.collect(SourceQuery(), config)
    assert len(items) > 0


# --- CachedPackageProvider ---

def test_cached_package_reads_json(tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    (cache_dir / "daily.json").write_text('[{"title": "Solar news", "content": "Test content", "url": "https://example.com"}]', encoding="utf-8")

    provider = CachedPackageProvider()
    config = {"enabled": True, "paths": [str(cache_dir)], "formats": ["json"]}
    items = provider.collect(SourceQuery(), config)
    assert len(items) == 1
    assert items[0].title == "Solar news"
    assert items[0].source_type == "cached"


def test_cached_package_reads_markdown(tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    (cache_dir / "notes.md").write_text("- Solar demand grew 10 percent in the first quarter of 2026\n- A new policy was announced that affects the solar industry\n", encoding="utf-8")

    provider = CachedPackageProvider()
    config = {"enabled": True, "paths": [str(cache_dir)], "formats": ["md"]}
    items = provider.collect(SourceQuery(), config)
    assert len(items) == 2


def test_cached_package_disabled():
    provider = CachedPackageProvider()
    items = provider.collect(SourceQuery(), {"enabled": False})
    assert items == []


# --- Full pipeline integration ---

def test_pipeline_with_provider_sources(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Create a local source file
    (input_dir / "news.md").write_text("- Solar industry expanded 15% in Q1.\n", encoding="utf-8")

    context = PipelineContext(
        project_name="Test Brief",
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        report_date="2026-06-02",
        max_source_age_days=14,
    )

    # Attach a SourceConfig to trigger provider-based collection
    source_config = SourceConfig(
        profile="research",
        industry="solar",
        enabled_providers=["manual"],
        manual={"enabled": True, "sources": [{"name": "Test", "path": str(input_dir), "enabled": True}]},
    )
    context.metadata["source_config"] = source_config

    outputs = BriefPipeline().run(context)

    # Should have source-collection + 6 agents = 7 outputs
    assert len(outputs) == 7
    assert outputs[0].agent_name == "source-collection"
    assert "2" in outputs[0].summary or "solar" in outputs[0].artifacts.get("industry", "")


def test_pipeline_backward_compatible_local_only(tmp_path):
    """Without source_config, pipeline falls back to local files."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    (input_dir / "news.md").write_text("- Test signal for backward compat.\n", encoding="utf-8")

    context = PipelineContext(
        project_name="Test",
        input_dir=str(input_dir),
        output_dir=str(output_dir),
    )

    outputs = BriefPipeline().run(context)
    assert len(outputs) == 7  # source-collection + 6 agents
    assert outputs[0].agent_name == "source-collection"


# --- P0: Scout should not overwrite provider sources ---

def test_scout_uses_provider_sources_when_available(tmp_path):
    """When context.sources is pre-populated by pipeline, Scout should use those."""
    from multi_agent_brief.agents.scout import ScoutAgent
    from multi_agent_brief.core.claim_ledger import ClaimLedger
    from multi_agent_brief.sources.base import SourceItem

    context = PipelineContext(
        project_name="Test",
        input_dir=str(tmp_path / "empty_input"),
        output_dir=str(tmp_path / "output"),
    )
    # Pre-populate sources as pipeline._collect_sources would
    context.sources = [
        SourceItem(
            source_id="PROVIDER_SRC",
            source_name="Provider Source",
            source_type="cached",
            title="Cached solar news",
            content="Solar manufacturing capacity expanded by 15 percent in Q1 2026 according to industry data.",
        ),
    ]

    ledger = ClaimLedger()
    agent = ScoutAgent()
    output = agent.run(context, ledger)

    assert len(ledger) > 0
    assert output.artifacts["source_count"] == 1
    # Claim should reference the provider source, not local files
    claims = list(ledger)
    assert claims[0].source_id == "PROVIDER_SRC"


def test_scout_falls_back_to_local_when_no_provider_sources(tmp_path):
    """When context.sources is empty, Scout should load from input_dir."""
    from multi_agent_brief.agents.scout import ScoutAgent
    from multi_agent_brief.core.claim_ledger import ClaimLedger

    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "news.md").write_text(
        "- A competitor announced a 2 GW manufacturing expansion plan.\n",
        encoding="utf-8",
    )

    context = PipelineContext(
        project_name="Test",
        input_dir=str(input_dir),
        output_dir=str(tmp_path / "output"),
    )
    assert context.sources == []  # empty

    ledger = ClaimLedger()
    agent = ScoutAgent()
    output = agent.run(context, ledger)

    assert len(ledger) > 0
    assert output.artifacts["source_count"] == 1
    claims = list(ledger)
    assert claims[0].source_type == "local_file"


def test_pipeline_provider_sources_appear_in_brief(tmp_path):
    """Full pipeline: provider sources should end up in the brief output."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    # Put only a README so local input has nothing useful
    (input_dir / "README.md").write_text("# Input directory\n", encoding="utf-8")

    # Create a cached package source
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    import json
    (cache_dir / "industry.json").write_text(json.dumps([
        {"title": "Solar expansion news", "content": "Global solar manufacturing capacity grew 15 percent in Q1 2026, reaching 800 GW annual throughput.", "url": "https://example.com/solar-expansion"},
    ]), encoding="utf-8")

    from multi_agent_brief.sources.base import SourceConfig
    source_config = SourceConfig(
        profile="research",
        industry="solar",
        enabled_providers=["cached_package"],
        cached_package={
            "enabled": True,
            "paths": [str(cache_dir)],
            "formats": ["json"],
        },
    )

    context = PipelineContext(
        project_name="Provider Test Brief",
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        report_date="2026-06-02",
        max_source_age_days=30,
    )
    context.metadata["source_config"] = source_config

    outputs = BriefPipeline().run(context)

    brief_text = (output_dir / "brief.md").read_text(encoding="utf-8")
    assert "solar" in brief_text.lower() or "capacity" in brief_text.lower()
    assert "[src:" in brief_text

    # Verify claim_ledger has the provider source claim
    import json as json_mod
    ledger_data = json_mod.loads((output_dir / "claim_ledger.json").read_text(encoding="utf-8"))
    assert len(ledger_data) > 0
    assert any("solar" in c["statement"].lower() or "capacity" in c["statement"].lower() for c in ledger_data)


# --- P1: manual_url placeholders should not become claims ---

def test_manual_url_placeholder_not_in_ledger(tmp_path):
    """Manual URL entries (placeholders) should be skipped by Scout."""
    from multi_agent_brief.agents.scout import ScoutAgent
    from multi_agent_brief.core.claim_ledger import ClaimLedger
    from multi_agent_brief.sources.base import SourceItem

    context = PipelineContext(
        project_name="Test",
        input_dir=str(tmp_path / "empty_input"),
        output_dir=str(tmp_path / "output"),
    )
    context.sources = [
        SourceItem(
            source_id="MANUAL_URL_1",
            source_name="PV Magazine",
            source_type="manual_url",
            title="PV Magazine",
            content="Manual URL source: https://www.pv-magazine.com/",
            url="https://www.pv-magazine.com/",
            metadata={"requires_fetch": True, "ingestion_status": "placeholder"},
        ),
        SourceItem(
            source_id="REAL_FILE",
            source_name="Real File",
            source_type="local_file",
            title="Real News",
            content="Solar demand grew 10 percent in Q1 2026 according to the latest industry report.",
        ),
    ]

    ledger = ClaimLedger()
    agent = ScoutAgent()
    agent.run(context, ledger)

    claims = list(ledger)
    # Only the real file should generate claims, not the placeholder URL
    assert all(c.source_id != "MANUAL_URL_1" for c in claims)
    assert any(c.source_id == "REAL_FILE" for c in claims)


# --- P0: Pipeline with no sources and no config still works (backward compat) ---

def test_pipeline_backward_compat_empty_input(tmp_path):
    """Pipeline with empty input dir and no source_config should still run."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    (input_dir / "README.md").write_text("# Empty\n", encoding="utf-8")

    context = PipelineContext(
        project_name="Empty Test",
        input_dir=str(input_dir),
        output_dir=str(output_dir),
    )

    outputs = BriefPipeline().run(context)
    # Should complete without error, with 7 outputs
    assert len(outputs) == 7
    assert (output_dir / "brief.md").exists()
