"""SourceHub Lite helpers for deterministic source setup."""

from __future__ import annotations

import glob
import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from multi_agent_brief.contracts.source_metadata import (
    normalize_source_category,
    source_url_error,
)

SOURCEHUB_TEXT_EXTENSIONS = {".json", ".md", ".txt"}
SOURCEHUB_MARKER = "sourcehub_lite"


class SourceHubError(Exception):
    """Raised when SourceHub Lite cannot update sources.yaml safely."""


@dataclass(frozen=True)
class SourceHubFilePlan:
    source: Path
    target: Path
    rel_target: str
    name: str
    sha256: str
    size_bytes: int


def add_file_sources(
    *,
    workspace: Path,
    values: list[str],
    source_category: str = "other",
    language: str = "en",
    name: str | None = None,
) -> dict[str, Any]:
    workspace = _require_workspace(workspace)
    sources_path = workspace / "sources.yaml"
    data = _load_sources_yaml(sources_path)
    source_paths = _resolve_file_inputs(values)
    plans = _plan_file_sources(
        workspace=workspace,
        source_paths=source_paths,
        single_name=name,
    )
    if not plans:
        raise SourceHubError("No source files matched.")

    category = normalize_source_category(source_category, default="other")
    manual = _ensure_mapping(data, "manual")
    existing = manual.get("sources")
    existing_sources = existing if isinstance(existing, list) else []
    next_sources = [
        item
        for item in existing_sources
        if isinstance(item, dict)
    ]
    existing_paths = {
        str(item.get("path") or "").strip()
        for item in next_sources
        if isinstance(item, dict)
    }
    added: list[dict[str, Any]] = []
    for plan in plans:
        if plan.rel_target in existing_paths:
            continue
        entry = {
            "name": plan.name,
            "path": plan.rel_target,
            "category": category,
            "language": language.strip() or "en",
            "enabled": True,
            "sourcehub_registered": True,
            "metadata": {
                "source_id": f"SH-{plan.sha256[:12].upper()}",
                "registered_by": SOURCEHUB_MARKER,
                "source_sha256": plan.sha256,
                "source_size_bytes": plan.size_bytes,
            },
        }
        next_sources.append(entry)
        existing_paths.add(plan.rel_target)
        added.append(
            {
                "name": plan.name,
                "path": plan.rel_target,
                "source_sha256": plan.sha256,
                "source_size_bytes": plan.size_bytes,
                "source_category": category,
            }
        )

    manual["enabled"] = True
    manual["sources"] = next_sources
    data["manual"] = manual
    _ensure_enabled_provider(data, "manual")

    # Copy source bytes only after sources.yaml has parsed and all targets are
    # planned. Persist only workspace-relative copied paths.
    for plan in plans:
        if plan.target.exists():
            if _sha256_file(plan.target) != plan.sha256:
                raise SourceHubError(
                    f"Refusing to overwrite existing source file: {plan.rel_target}"
                )
            continue
        plan.target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(plan.source, plan.target)

    _write_sources_yaml(sources_path, data)
    return {
        "ok": True,
        "action": "sources.add-file",
        "workspace": str(workspace),
        "source_count": len(added),
        "sources": added,
        "boundary": "sourcehub_lite_source_setup_only",
        "non_claims": [
            "no_source_collection_run",
            "no_hidden_web_crawling",
            "no_evidence_span_generation",
            "no_semantic_support_assessment",
        ],
    }


def add_rss_feed(
    *,
    workspace: Path,
    url: str,
    name: str | None = None,
    source_category: str = "news_media",
    language: str = "en",
) -> dict[str, Any]:
    workspace = _require_workspace(workspace)
    sources_path = workspace / "sources.yaml"
    data = _load_sources_yaml(sources_path)
    normalized_url = url.strip()
    error = source_url_error(normalized_url)
    if error:
        raise SourceHubError(f"RSS URL {error}: {normalized_url}")
    parsed = urlparse(normalized_url)
    feed_name = (name or parsed.netloc or normalized_url).strip()
    if not feed_name:
        raise SourceHubError("RSS feed name must be non-empty.")

    rss = _ensure_mapping(data, "rss")
    feeds = rss.get("feeds")
    next_feeds = (
        [item for item in feeds if isinstance(item, dict)]
        if isinstance(feeds, list)
        else []
    )
    category = normalize_source_category(source_category, default="news_media")
    feed_entry = {
        "name": feed_name,
        "url": normalized_url,
        "category": category,
        "language": language.strip() or "en",
        "enabled": True,
        "sourcehub_registered": True,
    }
    existing_index = _find_matching_index(next_feeds, key="url", value=normalized_url)
    if existing_index is None:
        next_feeds.append(feed_entry)
        added = True
        updated = False
    else:
        next_feeds[existing_index] = {**next_feeds[existing_index], **feed_entry}
        added = False
        updated = True
    rss["enabled"] = True
    rss["feeds"] = next_feeds
    data["rss"] = rss
    _ensure_enabled_provider(data, "rss")
    _write_sources_yaml(sources_path, data)
    return {
        "ok": True,
        "action": "sources.add-rss",
        "workspace": str(workspace),
        "feed_count": 1 if added else 0,
        "updated": updated,
        "feed": {
            **feed_entry,
            "source_category": category,
        },
        "boundary": "sourcehub_lite_source_setup_only",
    }


def add_web_search_handoff(
    *,
    workspace: Path,
    query: str,
    domains: list[str] | None = None,
    max_results: int = 10,
    recency_days: int | None = None,
) -> dict[str, Any]:
    workspace = _require_workspace(workspace)
    sources_path = workspace / "sources.yaml"
    data = _load_sources_yaml(sources_path)
    normalized_query = query.strip()
    if not normalized_query:
        raise SourceHubError("web search handoff query must be non-empty.")
    if max_results <= 0:
        raise SourceHubError("--max-results must be positive.")
    if recency_days is not None and recency_days <= 0:
        raise SourceHubError("--recency-days must be positive when set.")

    web_search = _ensure_mapping(data, "web_search")
    tasks = web_search.get("search_tasks")
    next_tasks = (
        [item for item in tasks if isinstance(item, dict)]
        if isinstance(tasks, list)
        else []
    )
    task = {
        "query": normalized_query,
        "max_results": max_results,
        "sourcehub_registered": True,
        "handoff_only": True,
    }
    clean_domains = [domain.strip() for domain in (domains or []) if domain.strip()]
    if clean_domains:
        task["domains"] = clean_domains
    if recency_days is not None:
        task["recency_days"] = recency_days
    existing_index = _find_matching_index(
        next_tasks,
        key="query",
        value=normalized_query,
    )
    if existing_index is None:
        next_tasks.append(task)
        added = True
        updated = False
    else:
        next_tasks[existing_index] = {**next_tasks[existing_index], **task}
        added = False
        updated = True

    web_search["enabled"] = True
    web_search["mode"] = "runtime_tool"
    web_search.pop("backend", None)
    web_search.pop("api_key_env", None)
    web_search["search_tasks"] = next_tasks
    data["web_search"] = web_search
    _ensure_enabled_provider(data, "web_search")
    _write_sources_yaml(sources_path, data)
    return {
        "ok": True,
        "action": "sources.add-web-search",
        "workspace": str(workspace),
        "task_count": 1 if added else 0,
        "updated": updated,
        "task": next_tasks[existing_index] if existing_index is not None else task,
        "boundary": "runtime_web_search_handoff_only",
        "non_claims": [
            "no_python_web_search_execution",
            "no_hidden_autonomous_crawler",
            "no_source_candidates_as_evidence",
        ],
    }


def project_sourcehub_handoff(workspace: Path) -> dict[str, Any]:
    """Project SourceHub Lite runtime setup into generated handoff artifacts."""
    ws = workspace.expanduser().resolve()
    sources_path = ws / "sources.yaml"
    if not sources_path.exists():
        return {"status": "not_available"}
    try:
        payload = _load_sources_yaml(sources_path)
    except (OSError, yaml.YAMLError, SourceHubError) as exc:
        return {
            "status": "invalid_sources_yaml",
            "source_config_path": "sources.yaml",
            "error": str(exc),
            "boundary": "sourcehub_lite_handoff_projection_only",
        }
    web_search = payload.get("web_search") if isinstance(payload.get("web_search"), dict) else {}
    runtime_tool = web_search.get("enabled") is True and web_search.get("mode") == "runtime_tool"
    search_tasks = (
        [
            _public_search_task(task)
            for task in (web_search.get("search_tasks") or [])
            if isinstance(task, dict) and str(task.get("query") or "").strip()
        ]
        if runtime_tool
        else []
    )
    manual = payload.get("manual") if isinstance(payload.get("manual"), dict) else {}
    rss = payload.get("rss") if isinstance(payload.get("rss"), dict) else {}
    sourcehub_file_count = sum(
        1
        for item in (manual.get("sources") or [])
        if isinstance(item, dict) and item.get("sourcehub_registered")
    )
    rss_feed_count = sum(
        1
        for item in (rss.get("feeds") or [])
        if isinstance(item, dict)
    )
    if not search_tasks and not sourcehub_file_count and not rss_feed_count:
        return {"status": "not_available"}
    return {
        "status": "available",
        "source_config_path": "sources.yaml",
        "boundary": "sourcehub_lite_handoff_projection_only",
        "runtime_effect": "handoff_only",
        "sourcehub_file_count": sourcehub_file_count,
        "rss_feed_count": rss_feed_count,
        "runtime_web_search": {
            "enabled": runtime_tool,
            "mode": web_search.get("mode") or "unknown",
            "task_count": len(search_tasks),
            "search_tasks": search_tasks,
        },
        "non_claims": [
            "no_python_web_search_execution",
            "no_hidden_autonomous_crawler",
            "no_source_candidates_as_evidence",
            "no_evidence_span_generation",
        ],
    }


def _find_matching_index(
    items: list[dict[str, Any]],
    *,
    key: str,
    value: str,
) -> int | None:
    for idx, item in enumerate(items):
        if str(item.get(key) or "").strip() == value:
            return idx
    return None


def _public_search_task(task: dict[str, Any]) -> dict[str, Any]:
    projected = {
        "query": str(task.get("query") or "").strip(),
        "max_results": _positive_int_or_default(
            task.get("max_results"),
            default=10,
        ),
        "handoff_only": bool(task.get("handoff_only")),
    }
    domains = [
        str(item).strip()
        for item in (task.get("domains") or [])
        if str(item).strip()
    ]
    if domains:
        projected["domains"] = domains
    if task.get("recency_days") is not None:
        projected["recency_days"] = task.get("recency_days")
    return projected


def _positive_int_or_default(value: Any, *, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _require_workspace(workspace: Path) -> Path:
    ws = workspace.expanduser().resolve()
    if not ws.exists() or not ws.is_dir():
        raise SourceHubError(f"workspace does not exist: {ws}")
    if not (ws / "config.yaml").exists():
        raise SourceHubError(f"config.yaml not found in workspace: {ws}")
    return ws


def _load_sources_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise SourceHubError("sources.yaml must contain a mapping.")
    return payload


def _write_sources_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _ensure_mapping(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if isinstance(value, dict):
        return value
    if value not in (None, ""):
        raise SourceHubError(f"{key} must be a mapping in sources.yaml.")
    return {}


def _ensure_enabled_provider(payload: dict[str, Any], provider: str) -> None:
    strategy = _ensure_mapping(payload, "source_strategy")
    enabled = strategy.get("enabled_providers")
    if isinstance(enabled, str):
        providers = [enabled]
    elif isinstance(enabled, list):
        providers = [str(item) for item in enabled if str(item).strip()]
    elif enabled is None:
        providers = []
    else:
        raise SourceHubError("source_strategy.enabled_providers must be a list.")
    if provider not in providers:
        providers.append(provider)
    strategy.setdefault("profile", "research")
    strategy["enabled_providers"] = providers
    payload["source_strategy"] = strategy


def _resolve_file_inputs(values: list[str]) -> list[Path]:
    paths: list[Path] = []
    for value in values:
        raw = str(value).strip()
        if not raw:
            continue
        expanded = str(Path(raw).expanduser())
        if any(token in raw for token in "*?[]"):
            matches = sorted(glob.glob(expanded))
            if not matches:
                raise SourceHubError(f"source glob matched no files: {raw}")
            paths.extend(Path(item) for item in matches)
        else:
            paths.append(Path(expanded))
    return paths


def _plan_file_sources(
    *,
    workspace: Path,
    source_paths: list[Path],
    single_name: str | None,
) -> list[SourceHubFilePlan]:
    if single_name and len(source_paths) != 1:
        raise SourceHubError("--name can only be used with one source file.")
    plans: list[SourceHubFilePlan] = []
    seen: set[Path] = set()
    for raw_path in source_paths:
        source = raw_path.expanduser().resolve()
        if source in seen:
            continue
        seen.add(source)
        if not source.exists() or not source.is_file():
            raise SourceHubError(f"source file not found: {raw_path}")
        extension = source.suffix.lower()
        if extension not in SOURCEHUB_TEXT_EXTENSIONS:
            raise SourceHubError(
                f"SourceHub Lite add-file supports text evidence only"
                f" ({', '.join(sorted(SOURCEHUB_TEXT_EXTENSIONS))}); got: {source.name}"
            )
        sha256 = _sha256_file(source)
        safe_name = _safe_filename(source.stem)
        target = workspace / "input" / "sources" / "sourcehub" / f"{safe_name}-{sha256[:12]}{extension}"
        display_name = (single_name or source.stem).strip() or source.name
        plans.append(
            SourceHubFilePlan(
                source=source,
                target=target,
                rel_target=_workspace_relative(workspace, target),
                name=display_name,
                sha256=sha256,
                size_bytes=source.stat().st_size,
            )
        )
    return plans


def _safe_filename(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in value.strip())
    safe = safe.strip(".-")
    return safe or "source"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _workspace_relative(workspace: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(workspace.resolve()).as_posix()
    except ValueError:
        return str(path)
