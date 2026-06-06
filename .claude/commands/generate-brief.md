---
description: Generate a real source-grounded brief using subagents and CLI finalize
argument-hint: "<workspace-path>"
---

You are generating a real user-facing brief for workspace: $ARGUMENTS.

MABW uses an external subagent workflow. Python CLI commands provide setup,
source discovery, input governance, audit checks, and final rendering tools.

Follow this sequence:

1. Read `$ARGUMENTS/config.yaml`, `$ARGUMENTS/sources.yaml`, `$ARGUMENTS/user.md`, and workspace inputs.

2. **Source discovery gate (llm_decide only):**
   If `sources.yaml` has `source_strategy.profile: llm_decide` and `source_candidates.yaml` does not exist or `metadata.status` is not `merged`:
   - If web search is enabled but unconfigured, explain supported options: Tavily, Exa, Brave, Firecrawl, Serper, runtime_websearch, or configure_later.
   - Run: `multi-agent-brief sources decide --config $ARGUMENTS/config.yaml`
   - Review `$ARGUMENTS/source_candidates.yaml`.
   - Run: `multi-agent-brief sources decide --config $ARGUMENTS/config.yaml --merge`
   - Only proceed after sources are resolved, OR if the user explicitly chooses local input-only mode.

3. **Doctor gate:**
   - Run: `multi-agent-brief doctor --config $ARGUMENTS/config.yaml`
   - Fix any issues before proceeding.

4. **Input governance gate (if available):**
   - Run: `multi-agent-brief inputs classify --config $ARGUMENTS/config.yaml`
   - Pass only evidence inputs to the scout subagent.
   - Treat feedback/instructions/context as non-evidence.

5. Invoke the **scout** subagent:
   - Read approved source materials, evidence inputs, and cached packages.
   - Extract candidate reportable items.
   - Write `$ARGUMENTS/output/intermediate/candidate_claims.json`.
   - Do not write final prose.

6. Invoke the **screener** subagent:
   - Dedupe, rank, freshness-check, and cap candidates.
   - Write `$ARGUMENTS/output/intermediate/screened_candidates.json`.

7. Invoke the **claim-ledger** subagent:
   - Convert screened candidates into source-grounded claims.
   - Write `$ARGUMENTS/output/intermediate/claim_ledger.json`.

8. Read `$ARGUMENTS/output/intermediate/claim_ledger.json` and `$ARGUMENTS/user.md`.

9. Invoke the **analyst** subagent:
   - Write the final brief from `claim_ledger.json` and `user.md`.
   - Use only `claim_ledger.json` as source evidence.
   - Preserve all valid `[src:CLAIM_ID]` citations.
   - Include dates for news items.
   - If `$ARGUMENTS/output/intermediate/market_competitor/analysis_cards.json` exists, read it and merge competitive analysis into the competitor section using `supporting_claim_ids` for `[src:CLAIM_ID]` citations.
   - Target a real weekly brief, not a thin bullet list.
   - Write the auditable brief to `$ARGUMENTS/output/intermediate/audited_brief.md`.

10. Invoke the **editor** subagent:
    - Polish for management / research team readability.
    - Remove invalid `[SRC:]`, `[SOURCE:]`, empty `[src:]`, and process residue.
    - Preserve valid `[src:CLAIM_ID]` in `audited_brief.md`.

11. Invoke the **auditor** subagent:
    - Audit `$ARGUMENTS/output/intermediate/audited_brief.md` against `$ARGUMENTS/output/intermediate/claim_ledger.json`.
    - Check orphan citations, unsupported facts, unsupported numbers, missing dates, investment advice language, and process residue.
    - Write/update `$ARGUMENTS/output/intermediate/audit_report.json`.

12. **Finalize:**
    - Run: `multi-agent-brief finalize --config $ARGUMENTS/config.yaml`
    - Confirm `output/brief.md` strips `[src:CLAIM_ID]`.
    - Confirm named Markdown / DOCX if configured.

13. **Final response:**
    - Report artifact paths.
    - Report audit status.
    - Report any remaining limitations.
    - Do not claim success if audit failed.
