from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DeliveryArtifact:
    path: str
    title: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeliveryTarget:
    channel: str
    recipient: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeliveryResult:
    connector_name: str
    delivered: bool
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class DeliveryConnector(ABC):
    name = "delivery-connector"

    @abstractmethod
    def deliver(self, artifact: DeliveryArtifact, target: DeliveryTarget) -> DeliveryResult:
        raise NotImplementedError

