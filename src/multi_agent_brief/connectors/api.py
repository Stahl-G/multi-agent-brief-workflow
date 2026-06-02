from __future__ import annotations

from multi_agent_brief.connectors.base import ConnectorResult, DataConnector, DataQuery


class ApiConnector(DataConnector):
    """Migration-track interface for authenticated or public APIs."""

    name = "api"

    def fetch(self, query: DataQuery) -> ConnectorResult:
        return ConnectorResult(
            connector_name=self.name,
            sources=[],
            metadata={"status": "interface_only", "query": query.query},
        )

