from multi_agent_brief.agents.auditor import AuditorAgent
from multi_agent_brief.audit.deterministic import DeterministicAuditAgent
from multi_agent_brief.audit.interfaces import CompositeAuditAgent
from multi_agent_brief.audit.semantic import NoOpSemanticAuditAgent, SemanticAuditPromptBuilder
from multi_agent_brief.core.claim_ledger import ClaimLedger
from multi_agent_brief.core.schemas import Claim, PipelineContext


def test_auditor_agent_delegates_to_audit_interface():
    ledger = ClaimLedger(
        [
            Claim(
                claim_id="SRC_ABCDEF",
                statement="A synthetic source reported a 2 GW expansion.",
                source_id="SRC",
                evidence_text="A synthetic source reported a 2 GW expansion.",
            )
        ]
    )
    context = PipelineContext(project_name="Demo", input_dir="input", output_dir="output")
    context.report_state.draft_markdown = "- A synthetic source reported a 2 GW expansion. [src:SRC_ABCDEF]"

    audit_agent = CompositeAuditAgent(DeterministicAuditAgent(), NoOpSemanticAuditAgent())
    result = AuditorAgent(audit_agent=audit_agent).run(context, ledger)

    assert result.artifacts["audit_status"] == "pass"
    assert context.report_state.audit_report.metadata["semantic_agent"] == "noop-semantic-auditor"


def test_semantic_prompt_builder_includes_claim_evidence():
    ledger = ClaimLedger(
        [
            Claim(
                claim_id="SRC_ABCDEF",
                statement="A synthetic source reported a 2 GW expansion.",
                source_id="SRC",
                evidence_text="Evidence text here.",
            )
        ]
    )

    prompt = SemanticAuditPromptBuilder().build_prompt("Draft [src:SRC_ABCDEF]", ledger)

    assert "SRC_ABCDEF" in prompt
    assert "Evidence text here." in prompt

