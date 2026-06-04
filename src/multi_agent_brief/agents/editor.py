from __future__ import annotations

from multi_agent_brief.agents.base import BaseAgent
from multi_agent_brief.agents.draft_cleanup import clean_process_residue
from multi_agent_brief.core.claim_ledger import ClaimLedger
from multi_agent_brief.core.schemas import AgentOutput, PipelineContext


class EditorAgent(BaseAgent):
    name = "editor"

    def run(self, context: PipelineContext, ledger: ClaimLedger) -> AgentOutput:
        draft = context.report_state.draft_markdown
        # Remove process residue ([SRC:], [SOURCE:], empty [src:], Claude/Codex logs).
        # Valid [src:CLAIM_ID] citations are intentionally PRESERVED so the final
        # brief remains traceable to Claim Ledger and auditable.
        cleaned = clean_process_residue(draft)
        context.report_state.prepared_markdown = cleaned
        return AgentOutput(agent_name=self.name, summary="Cleaned draft Markdown for review.")
