"""Web search source provider with pluggable backends."""
from __future__ import annotations

import hashlib
from typing import Any

from multi_agent_brief.sources.base import SourceItem, SourceProvider, SourceQuery
from multi_agent_brief.sources.search_backends.base import SearchBackend, SearchResult


class WebSearchProvider(SourceProvider):
    """Web search provider using pluggable search backends."""

    name = "web_search"
    source_type = "web_search"

    def __init__(self, backend: SearchBackend | None = None) -> None:
        self._backend = backend

    def _get_backend(self, config: dict[str, Any]) -> SearchBackend:
        if self._backend is not None:
            return self._backend
        backend_name = config.get("backend") or ""
        if not backend_name:
            raise RuntimeError("web_search is enabled but no backend is configured.")
        raise NotImplementedError(
            f"web_search backend '{backend_name}' is not implemented in this package. "
            "Use a connector/provider or inject a SearchBackend implementation."
        )

    def validate_config(self, config: dict[str, Any]) -> list[str]:
        if not config.get("enabled"):
            return []
        try:
            backend = self._get_backend(config)
        except (RuntimeError, NotImplementedError) as exc:
            return [str(exc)]
        if not backend.is_available():
            return [f"web_search: backend '{backend.name}' is not available"]
        return []

    def collect(self, query: SourceQuery, config: dict[str, Any]) -> list[SourceItem]:
        if not config.get("enabled"):
            return []

        backend = self._get_backend(config)
        if not backend.is_available():
            return []

        all_items: list[SourceItem] = []
        max_results = config.get("max_results", 20)

        # Build search queries from query keywords or config
        queries = self._build_queries(query, config)

        for q, domains in queries:
            results = backend.search(q, max_results=max_results, domains=domains)
            for r in results:
                item = self._result_to_source_item(r, q)
                all_items.append(item)

        return all_items

    def _build_queries(self, query: SourceQuery, config: dict[str, Any]) -> list[tuple[str, list[str] | None]]:
        """Build search queries from the query object and config.

        Returns list of (query_string, domains_or_none) tuples.
        """
        queries: list[tuple[str, list[str] | None]] = []

        # Use query keywords if provided
        if query.keywords:
            queries.append((" ".join(query.keywords), None))

        # Use pre-defined queries from config
        for task in config.get("search_tasks", []):
            q = task.get("query", "")
            if q:
                domains = task.get("domains") or None
                queries.append((q, domains))

        # Fallback: generic query
        if not queries:
            queries.append(("latest news", None))

        return queries

    def _result_to_source_item(self, result: SearchResult, query: str) -> SourceItem:
        """Convert a SearchResult to a SourceItem."""
        raw = f"{result.url}|{result.title}"
        digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10].upper()
        source_id = f"WS_{digest}"
        return SourceItem(
            source_id=source_id,
            source_name=result.source_name or "web_search",
            source_type="web_search",
            title=result.title,
            content=result.snippet,
            url=result.url,
            published_at=result.published_at,
            reliability="medium",
            metadata={"query": query, "backend": self._get_backend({}).name},
        )
