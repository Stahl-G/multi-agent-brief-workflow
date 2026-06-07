---
description: Generate a real source-grounded and audited brief
agent: brief-orchestrator
subtask: false
---

You are generating a real user-facing brief for workspace: $ARGUMENTS

MABW uses an external subagent workflow. Python CLI commands provide setup,
source discovery, input governance, audit checks, and final rendering tools.

Follow this sequence:

1. Read `$ARGUMENTS/config.yaml`, `$ARGUMENTS/sources.yaml`, `$ARGUMENTS/user.md`, and workspace inputs.

2. **Source discovery gate (llm_decide only):**
   If `sources.yaml` has `source.mode: llm_decide` and `source_candidates.yaml` does not exist or has not been merged:
   - Run: `multi-agent-brief sources decide --config $ARGUMENTS/config.yaml`
   - Review `$ARGUMENTS/source_candidates.yaml`.
   - Run: `multi-agent-brief sources decide --config $ARGUMENTS/config.yaml --merge`

3. **Doctor gate:**
   - Run: `multi-agent-brief doctor --config $ARGUMENTS/config.yaml`
   - Fix any issues before proceeding.

4. **Input governance gate:**
   - Run: `multi-agent-brief inputs classify --config $ARGUMENTS/config.yaml`
   - Pass only evidence inputs to the scout subagent.

5. Invoke the **scout** subagent:
   - Read approved source materials, evidence inputs, and cached packages.
   - Extract candidate reportable items.
   - Write `$ARGUMENTS/output/intermediate/candidate_claims.json`.

6. Invoke the **screener** subagent:
   - Dedupe, rank, freshness-check, and cap candidates.
   - Write `$ARGUMENTS/output/intermediate/screened_candidates.json`.

7. Invoke the **claim-ledger** subagent:
   - Convert screened candidates into source-grounded claims.
   - Write `$ARGUMENTS/output/intermediate/claim_ledger.json`.

8. Read `$ARGUMENTS/output/intermediate/claim_ledger.json` and `$ARGUMENTS/user.md`.

9. Invoke the **brief-analyst** subagent:
   - Write the final brief from `claim_ledger.json` and `user.md`.
   - Use only `claim_ledger.json` as source evidence.
   - Preserve all valid [src:CLAIM_ID] citations.
   - Write the auditable brief to `$ARGUMENTS/output/intermediate/audited_brief.md`.

10. Invoke the **brief-editor** subagent:
    - Polish for management / research team readability.
    - Preserve valid [src:CLAIM_ID] in `audited_brief.md`.

11. Invoke the **brief-auditor** subagent:
    - Audit `$ARGUMENTS/output/intermediate/audited_brief.md` against `$ARGUMENTS/output/intermediate/claim_ledger.json`.

12. **Finalize:**
    - Run: `multi-agent-brief finalize --config $ARGUMENTS/config.yaml`
    - Confirm `output/brief.md` strips [src:CLAIM_ID].

13. **Final response:**
    - Report artifact paths.
    - Report audit status.
    - Report success when audit status supports delivery.
