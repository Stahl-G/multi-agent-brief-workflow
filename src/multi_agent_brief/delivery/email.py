from __future__ import annotations

from multi_agent_brief.delivery.base import DeliveryArtifact, DeliveryConnector, DeliveryResult, DeliveryTarget


class EmailDeliveryConnector(DeliveryConnector):
    name = "email"

    def deliver(self, artifact: DeliveryArtifact, target: DeliveryTarget) -> DeliveryResult:
        return DeliveryResult(self.name, False, "Interface only; configure an implementation before use.")

