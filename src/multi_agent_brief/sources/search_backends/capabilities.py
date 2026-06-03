"""Search backend capability abstraction.

Describes what a search backend can do without requiring live API calls.
Used by the source planner and provider registry to make informed decisions
about which backend to use for different search tasks.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchBackendCapabilities:
    """Describes the capabilities of a search backend.

    This is a pure description — no API calls, no side effects.
    Used by the planner to route queries to the best backend.
    """

    name: str
    kind: str  # "ai_search" | "serp" | "search_plus_extract" | "answer_api"

    # Content type support
    supports_news: bool = False
    supports_domains: bool = False
    supports_date_filter: bool = False
    supports_raw_content: bool = False
    supports_highlights: bool = False
    supports_verticals: bool = False
    supports_financial_reports: bool = False
    supports_research_papers: bool = False
    supports_patents: bool = False

    # Quality indicators
    published_at_quality: str = "weak"  # "good" | "partial" | "weak"
    evidence_quality: str = "snippet"  # "snippet" | "highlight" | "full_text"


# Pre-defined capabilities for known backends
TAVILY_CAPABILITIES = SearchBackendCapabilities(
    name="tavily",
    kind="ai_search",
    supports_news=True,
    supports_domains=True,
    supports_date_filter=True,
    supports_raw_content=True,
    published_at_quality="partial",
    evidence_quality="snippet",
)

EXA_CAPABILITIES = SearchBackendCapabilities(
    name="exa",
    kind="ai_search",
    supports_news=True,
    supports_domains=True,
    supports_date_filter=True,
    supports_highlights=True,
    supports_research_papers=True,
    supports_financial_reports=True,
    published_at_quality="good",
    evidence_quality="highlight",
)

BRAVE_CAPABILITIES = SearchBackendCapabilities(
    name="brave",
    kind="serp",
    supports_news=True,
    supports_domains=True,
    supports_date_filter=True,
    published_at_quality="partial",
    evidence_quality="snippet",
)

FIRECRAWL_CAPABILITIES = SearchBackendCapabilities(
    name="firecrawl",
    kind="search_plus_extract",
    supports_domains=True,
    supports_raw_content=True,
    published_at_quality="weak",
    evidence_quality="full_text",
)

SERPER_CAPABILITIES = SearchBackendCapabilities(
    name="serper",
    kind="serp",
    supports_news=True,
    supports_domains=True,
    supports_date_filter=True,
    supports_verticals=True,
    supports_research_papers=True,
    supports_patents=True,
    published_at_quality="partial",
    evidence_quality="snippet",
)
