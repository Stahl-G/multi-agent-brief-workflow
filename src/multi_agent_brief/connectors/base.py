from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from multi_agent_brief.core.schemas import SourceItem


@dataclass
class DataQuery:
    query: str = ""
    start_date: str = ""
    end_date: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConnectorResult:
    connector_name: str
    sources: list[SourceItem]
    metadata: dict[str, Any] = field(default_factory=dict)


class DataConnector(ABC):
    name = "data-connector"

    @abstractmethod
    def fetch(self, query: DataQuery) -> ConnectorResult:
        raise NotImplementedError

