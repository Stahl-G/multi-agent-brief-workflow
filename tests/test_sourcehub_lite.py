"""Tests for the SourceHub Lite source setup commands."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from multi_agent_brief.cli.main import main
from multi_agent_brief.sources.registry import collect_all_sources, load_sources_config


def _workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "workspace"
    ws.mkdir()
    (ws / "config.yaml").write_text("project:\n  name: Test\n", encoding="utf-8")
    (ws / "sources.yaml").write_text(
        "source_strategy:\n"
        "  profile: conservative\n"
        "  enabled_providers:\n"
        "    - manual\n"
        "manual:\n"
        "  enabled: true\n"
        "  sources: []\n"
        "web_search:\n"
        "  enabled: false\n"
        "  mode: disabled\n",
        encoding="utf-8",
    )
    return ws


def test_sources_add_file_copies_text_source_without_external_path_leak(
    tmp_path: Path,
    capsys,
) -> None:
    ws = _workspace(tmp_path)
    outside = tmp_path / "outside-user-folder"
    outside.mkdir()
    source = outside / "market-note.md"
    source.write_text("# Market Note\n\nPrice moved.\n", encoding="utf-8")

    rc = main(
        [
            "sources",
            "add-file",
            "--workspace",
            str(ws),
            "--category",
            "market_report",
            "--json",
            str(source),
        ]
    )
    assert rc == 0
    output = capsys.readouterr().out
    payload = json.loads(output)
    assert payload["ok"] is True
    assert payload["source_count"] == 1
    assert str(source) not in output
    assert "outside-user-folder" not in output

    sources_text = (ws / "sources.yaml").read_text(encoding="utf-8")
    assert str(source) not in sources_text
    assert "outside-user-folder" not in sources_text
    data = yaml.safe_load(sources_text)
    entry = data["manual"]["sources"][0]
    assert entry["path"].startswith("input/sources/sourcehub/")
    assert entry["category"] == "market_report"
    copied = ws / entry["path"]
    assert copied.read_text(encoding="utf-8").startswith("# Market Note")

    source_config = load_sources_config(ws / "sources.yaml")
    items, errors = collect_all_sources(source_config)
    assert errors == []
    assert len(items) == 1
    assert items[0].source_type == "local_file"


def test_sources_add_file_expands_home_globs(tmp_path: Path, monkeypatch, capsys) -> None:
    ws = _workspace(tmp_path)
    home = tmp_path / "home"
    docs = home / "docs"
    docs.mkdir(parents=True)
    (docs / "one.md").write_text("# One\n", encoding="utf-8")
    (docs / "two.txt").write_text("Two\n", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))

    rc = main(
        [
            "sources",
            "add-file",
            "--workspace",
            str(ws),
            "~/docs/*",
        ]
    )
    assert rc == 0
    capsys.readouterr()
    data = yaml.safe_load((ws / "sources.yaml").read_text(encoding="utf-8"))
    paths = [item["path"] for item in data["manual"]["sources"]]
    assert len(paths) == 2
    assert all(path.startswith("input/sources/sourcehub/") for path in paths)


def test_sources_add_file_rejects_binary_without_writing(tmp_path: Path, capsys) -> None:
    ws = _workspace(tmp_path)
    binary = tmp_path / "deck.pdf"
    binary.write_bytes(b"%PDF-1.4")

    rc = main(["sources", "add-file", "--workspace", str(ws), str(binary)])
    assert rc == 1
    output = capsys.readouterr().out
    assert "text evidence only" in output
    assert not (ws / "input" / "sources" / "sourcehub").exists()
    data = yaml.safe_load((ws / "sources.yaml").read_text(encoding="utf-8"))
    assert data["manual"]["sources"] == []


def test_sources_add_rss_registers_feed(tmp_path: Path, capsys) -> None:
    ws = _workspace(tmp_path)
    rc = main(
        [
            "sources",
            "add-rss",
            "--workspace",
            str(ws),
            "--name",
            "Industry Feed",
            "https://example.com/feed.xml",
        ]
    )
    assert rc == 0
    capsys.readouterr()
    data = yaml.safe_load((ws / "sources.yaml").read_text(encoding="utf-8"))
    assert "rss" in data["source_strategy"]["enabled_providers"]
    assert data["rss"]["enabled"] is True
    assert data["rss"]["feeds"][0]["url"] == "https://example.com/feed.xml"
    assert data["rss"]["feeds"][0]["category"] == "news_media"


def test_sources_add_rss_duplicate_updates_and_reports_persisted_feed(
    tmp_path: Path,
    capsys,
) -> None:
    ws = _workspace(tmp_path)
    assert main([
        "sources",
        "add-rss",
        "--workspace",
        str(ws),
        "--name",
        "Old Feed",
        "https://example.com/feed.xml",
        "--json",
    ]) == 0
    capsys.readouterr()

    rc = main([
        "sources",
        "add-rss",
        "--workspace",
        str(ws),
        "--name",
        "New Feed",
        "--category",
        "market_report",
        "https://example.com/feed.xml",
        "--json",
    ])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["updated"] is True
    assert payload["feed_count"] == 0
    assert payload["feed"]["name"] == "New Feed"
    assert payload["feed"]["source_category"] == "market_report"

    data = yaml.safe_load((ws / "sources.yaml").read_text(encoding="utf-8"))
    assert len(data["rss"]["feeds"]) == 1
    assert data["rss"]["feeds"][0]["name"] == "New Feed"
    assert data["rss"]["feeds"][0]["category"] == "market_report"


def test_sources_add_rss_rejects_invalid_url(tmp_path: Path, capsys) -> None:
    ws = _workspace(tmp_path)
    rc = main(["sources", "add-rss", "--workspace", str(ws), "not a url"])
    assert rc == 1
    assert "http(s)" in capsys.readouterr().out
    data = yaml.safe_load((ws / "sources.yaml").read_text(encoding="utf-8"))
    assert "rss" not in data.get("source_strategy", {}).get("enabled_providers", [])


def test_sources_add_web_search_is_runtime_handoff_only(tmp_path: Path, capsys) -> None:
    ws = _workspace(tmp_path)
    rc = main(
        [
            "sources",
            "add-web-search",
            "--workspace",
            str(ws),
            "--query",
            "solar module prices latest",
            "--domain",
            "example.com",
            "--recency-days",
            "7",
        ]
    )
    assert rc == 0
    output = capsys.readouterr().out
    assert "no Python search was run" in output
    data = yaml.safe_load((ws / "sources.yaml").read_text(encoding="utf-8"))
    assert "web_search" in data["source_strategy"]["enabled_providers"]
    assert data["web_search"]["enabled"] is True
    assert data["web_search"]["mode"] == "runtime_tool"
    assert "backend" not in data["web_search"]
    assert data["web_search"]["search_tasks"][0]["handoff_only"] is True
    source_config = load_sources_config(ws / "sources.yaml")
    items, errors = collect_all_sources(source_config)
    assert items == []
    assert errors == []


def test_sources_add_web_search_duplicate_updates_and_reports_persisted_task(
    tmp_path: Path,
    capsys,
) -> None:
    ws = _workspace(tmp_path)
    assert main([
        "sources",
        "add-web-search",
        "--workspace",
        str(ws),
        "--query",
        "solar prices",
        "--domain",
        "old.example",
        "--max-results",
        "10",
        "--json",
    ]) == 0
    capsys.readouterr()

    rc = main([
        "sources",
        "add-web-search",
        "--workspace",
        str(ws),
        "--query",
        "solar prices",
        "--domain",
        "new.example",
        "--max-results",
        "25",
        "--json",
    ])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["updated"] is True
    assert payload["task_count"] == 0
    assert payload["task"]["domains"] == ["new.example"]
    assert payload["task"]["max_results"] == 25

    data = yaml.safe_load((ws / "sources.yaml").read_text(encoding="utf-8"))
    tasks = data["web_search"]["search_tasks"]
    assert len(tasks) == 1
    assert tasks[0]["domains"] == ["new.example"]
    assert tasks[0]["max_results"] == 25


def test_sourcehub_bad_sources_yaml_fails_without_copying(tmp_path: Path, capsys) -> None:
    ws = _workspace(tmp_path)
    (ws / "sources.yaml").write_text("source_strategy: [\n", encoding="utf-8")
    source = tmp_path / "source.md"
    source.write_text("# Source\n", encoding="utf-8")

    rc = main(["sources", "add-file", "--workspace", str(ws), str(source)])
    assert rc == 1
    assert "while parsing" in capsys.readouterr().out
    assert not (ws / "input" / "sources" / "sourcehub").exists()
