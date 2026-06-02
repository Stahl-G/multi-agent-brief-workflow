from __future__ import annotations

from abc import ABC, abstractmethod

from multi_agent_brief.core.claim_ledger import ClaimLedger
from multi_agent_brief.core.schemas import AuditReport, PipelineContext


class AuditAgentInterface(ABC):
    """Backend interface used by the pipeline AuditorAgent."""

    name = "audit-agent"

    @abstractmethod
    def run_audit(
        self,
        markdown: str,
        ledger: ClaimLedger,
        context: PipelineContext | None = None,
    ) -> AuditReport:
        raise NotImplementedError


class CompositeAuditAgent(AuditAgentInterface):
    """Runs deterministic audit first, then optional semantic audit."""

    name = "composite-auditor"

    def __init__(
        self,
        deterministic_agent: AuditAgentInterface,
        semantic_agent: AuditAgentInterface | None = None,
    ) -> None:
        self.deterministic_agent = deterministic_agent
        self.semantic_agent = semantic_agent

    def run_audit(
        self,
        markdown: str,
        ledger: ClaimLedger,
        context: PipelineContext | None = None,
    ) -> AuditReport:
        report = self.deterministic_agent.run_audit(markdown, ledger, context)
        report.metadata["deterministic_agent"] = self.deterministic_agent.name

        if self.semantic_agent is None:
            report.metadata["semantic_agent"] = "not_configured"
            return report

        semantic_report = self.semantic_agent.run_audit(markdown, ledger, context)
        report.findings.extend(semantic_report.findings)
        report.metadata["semantic_agent"] = self.semantic_agent.name
        report.metadata["semantic_findings"] = len(semantic_report.findings)

        high = sum(1 for finding in report.findings if finding.severity == "high")
        medium = sum(1 for finding in report.findings if finding.severity == "medium")
        if high:
            report.audit_status = "fail"
        elif medium:
            report.audit_status = "warning"
        else:
            report.audit_status = "pass"
        report.audit_score = max(0, 100 - high * 25 - medium * 10 - (len(report.findings) - high - medium) * 3)
        return report

