"""Search backends for web search provider."""
from multi_agent_brief.sources.search_backends.base import SearchBackend, SearchResult
from multi_agent_brief.sources.search_backends.brave import BraveBackend
from multi_agent_brief.sources.search_backends.capabilities import (
    BRAVE_CAPABILITIES,
    EXA_CAPABILITIES,
    SearchBackendCapabilities,
    TAVILY_CAPABILITIES,
)
from multi_agent_brief.sources.search_backends.exa import ExaBackend
from multi_agent_brief.sources.search_backends.tavily import TavilyBackend

__all__ = [
    "BraveBackend",
    "BRAVE_CAPABILITIES",
    "ExaBackend",
    "EXA_CAPABILITIES",
    "SearchBackend",
    "SearchBackendCapabilities",
    "SearchResult",
    "TavilyBackend",
    "TAVILY_CAPABILITIES",
]
