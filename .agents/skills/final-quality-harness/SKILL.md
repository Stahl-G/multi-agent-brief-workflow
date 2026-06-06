---
name: final-quality-harness
description: Reviews and implements final text delivery gates for BRIEF_HARNESS_V2 final target. Use when working on FinalQualityAuditAgent, final Markdown quality gates, report depth, metadata, summary bullet separation, stale-current framing, or publication readiness.
---

# Final Quality Harness Skill

## Purpose

Reviews and implements final text delivery gates for BRIEF_HARNESS_V2 final target.

## When To Use

Use when working on FinalQualityAuditAgent, final Markdown quality gates, report depth, metadata, summary bullet separation, stale-current framing, or publication readiness.

## Responsibilities

- Validate final report depth unless quiet_week is explicit.
- Validate front-page metadata when configured.
- Validate executive summary bullet separation.
- Block stale-current framing.
- Block internal workflow residue.
- Keep final gate separate from default MVP draft audit.

## Guardrails

- Require final text quality gates in addition to factual correctness.
- Repair final prose within existing evidence.
- Preserve required safety notes during formatting fixes.

## Subagent workflow Context

```text
Scout -> Screener -> Claim Ledger -> Analyst -> Editor -> Auditor -> Formatter
```

## Expected Inputs

Source files, claim ledger entries, or draft markdown as appropriate for the harness stage.

## Expected Outputs

Structured artifacts conforming to the workflow contract:
- `draft_brief.md`
- `claim_ledger.json`
- `audit_report.json`
- `source_map.md`
