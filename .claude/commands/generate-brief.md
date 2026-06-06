---
description: Generate a real source-grounded brief using explicit Claude Code subagents
argument-hint: "<workspace-path>"
---

You are generating a real user-facing brief for workspace: $ARGUMENTS.

MABW uses an external subagent workflow. Python CLI commands provide setup, source planning, validation, audit checks, and final rendering tools.

Follow this sequence:

1. Read:
   - $ARGUMENTS/config.yaml
   - $ARGUMENTS/user.md
   - $ARGUMENTS/sources.yaml
   - workspace input/source files

2. **Source discovery gate (llm_decide only):**
   If `sources.yaml` has `source_strategy.profile: llm_decide` and `source_candidates.yaml` is missing or unmerged, resolve sources before invoking Scout:
   - Explain supported web-search options neutrally: Tavily, Exa, Brave, Firecrawl, Serper, runtime_websearch, or configure_later.
   - Run `multi-agent-brief sources decide --config $ARGUMENTS/config.yaml`.
   - Review `$ARGUMENTS/source_candidates.yaml`.
   - Run `multi-agent-brief sources decide --config $ARGUMENTS/config.yaml --merge` after source approval.
   - Local input-only mode can proceed directly to the doctor gate.

3. **Doctor gate:**
   - Run `multi-agent-brief doctor --config $ARGUMENTS/config.yaml`.
   - Resolve reported issues before proceeding.

4. **Input governance gate (if available):**
   - Run `multi-agent-brief inputs classify --config $ARGUMENTS/config.yaml`.
   - Give the scout subagent the evidence input list.
   - Give user feedback, instructions, and context files to the relevant subagents as guidance rather than factual evidence.

5. Invoke the **scout** subagent:
   - Read approved workspace sources, evidence inputs, and cached packages.
   - Extract candidate reportable items.
   - Write `$ARGUMENTS/output/intermediate/candidate_claims.json`.

6. Invoke the **screener** subagent:
   - Rank, deduplicate, freshness-check, and capacity-cap candidate items.
   - Write `$ARGUMENTS/output/intermediate/screened_candidates.json`.

7. Invoke the **claim-ledger** subagent:
   - Convert screened candidates into stable, source-grounded claims.
   - Write `$ARGUMENTS/output/intermediate/claim_ledger.json`.

8. **Market & Competitor Module (if enabled):**
   - Check whether `$ARGUMENTS/competitor_universe.yaml` has non-empty entities.
   - If the module is enabled in config.yaml, use the market-competitor subagents to generate analysis cards and audit findings.
   - Merge supported competitive analysis through Claim Ledger citations.

9. Invoke the **analyst** subagent:
   - Read `$ARGUMENTS/output/intermediate/claim_ledger.json` and `$ARGUMENTS/user.md`.
   - Write the auditable brief using Claim Ledger evidence.
   - Preserve valid `[src:CLAIM_ID]` citations.
   - Include dates for news items.
   - Write `$ARGUMENTS/output/intermediate/audited_brief.md`.

10. Invoke the **editor** subagent:
    - Polish for management or research-team readability.
    - Clean invalid citation markers and process residue.
    - Preserve valid `[src:CLAIM_ID]` citations in `audited_brief.md`.

11. Invoke the **auditor** subagent:
    - Audit `$ARGUMENTS/output/intermediate/audited_brief.md` against `$ARGUMENTS/output/intermediate/claim_ledger.json`.
    - Check citation support, numbers, dates, advice language, and process residue.
    - Write or update `$ARGUMENTS/output/intermediate/audit_report.json`.

12. Invoke the **formatter** subagent / finalize tool:
    - Run `multi-agent-brief finalize --config $ARGUMENTS/config.yaml`.
    - Confirm `$ARGUMENTS/output/brief.md` is reader-facing.
    - Confirm the configured named Markdown copy exists if enabled.
    - Confirm `$ARGUMENTS/output/brief.docx` exists if DOCX is configured.

13. Final response:
    - Report artifact paths.
    - Report audit status.
    - Report remaining limitations.
