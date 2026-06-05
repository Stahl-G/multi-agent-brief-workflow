---
description: Generate a real source-grounded and audited brief
agent: brief-orchestrator
subtask: false
---

You are generating a real user-facing brief for workspace: $ARGUMENTS

The Python CLI prepares deterministic reader-facing files and intermediate audit artifacts. A polished final brief should still be reviewed by OpenCode subagents or a human using the Claim Ledger and audit outputs.

Follow this sequence exactly:

1. Read:
   - $ARGUMENTS/config.yaml
   - $ARGUMENTS/user.md
   - $ARGUMENTS/sources.yaml

2. **Source discovery gate (llm_decide only):**
   If `sources.yaml` has `source.mode: llm_decide` and `source_candidates.yaml` does not exist or has not been merged, resolve sources before running the pipeline:
   - Run: `multi-agent-brief sources decide --config $ARGUMENTS/config.yaml`
   - Review the generated `$ARGUMENTS/source_candidates.yaml`.
   - Run: `multi-agent-brief sources decide --config $ARGUMENTS/config.yaml --merge`

3. **Prepare deterministic pipeline artifacts:**
   - Run: `multi-agent-brief doctor --config $ARGUMENTS/config.yaml`
   - Fix any issues before proceeding.
   - Run: `multi-agent-brief prepare --config $ARGUMENTS/config.yaml`

4. Read:
   - $ARGUMENTS/output/intermediate/claim_ledger.json
   - $ARGUMENTS/output/intermediate/audited_brief.md
   - $ARGUMENTS/user.md

5. Invoke the **brief-analyst** subagent:
   - Write the final brief from claim_ledger.json and user.md.
   - Use only claim_ledger.json as source evidence.
   - Preserve all valid [src:CLAIM_ID] citations.
   - Write the auditable brief to $ARGUMENTS/output/intermediate/audited_brief.md.

6. Invoke the **brief-editor** subagent:
   - Polish for management / research team readability.
   - Preserve valid [src:CLAIM_ID] in audited_brief.md.

7. Invoke the **brief-auditor** subagent:
   - Audit $ARGUMENTS/output/intermediate/audited_brief.md against $ARGUMENTS/output/intermediate/claim_ledger.json.

8. Regenerate DOCX:
   - Regenerate $ARGUMENTS/output/brief.md by stripping [src:CLAIM_ID] from the audited brief.

9. Final response:
   - Report artifact paths.
   - Report audit status.
   - Do not claim success if audit failed.
