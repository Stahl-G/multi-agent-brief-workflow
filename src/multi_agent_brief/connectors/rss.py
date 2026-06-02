from __future__ import annotations

from multi_agent_brief.connectors.base import ConnectorResult, DataConnector, DataQuery


class RssConnector(DataConnector):
    """Migration-track interface for RSS ingestion."""

    name = "rss"

    def fetch(self, query: DataQuery) -> ConnectorResult:
        return ConnectorResult(
            connector_name=self.name,
            sources=[],
            metadata={"status": "interface_only", "query": query.query},
        )

