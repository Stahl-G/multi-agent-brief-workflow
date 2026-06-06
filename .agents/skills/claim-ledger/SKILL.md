---
name: claim-ledger
description: Converts screened candidates into source-grounded claim ledger entries with stable IDs and evidence. Use when implementing or reviewing claim ID creation, source evidence storage, claim metadata, or ledger consistency.
---

# Claim Ledger Skill

## Purpose

Converts screened candidates into source-grounded claim ledger entries with stable IDs and evidence.

## When To Use

Use when implementing or reviewing claim ID creation, source evidence storage, claim metadata, or ledger consistency.

## Responsibilities

- Create stable claim IDs.
- Ensure every claim has source evidence.
- Preserve source IDs and evidence text.
- Carry useful Screener metadata forward.
- Detect duplicate or unsupported claims.

## Guardrails

- Every claim must be evidence-backed.
- Merge claims only when traceability is preserved.
- Keep language strength aligned with evidence strength.

## Subagent workflow Context

```text
Scout -> Screener -> Claim Ledger -> Analyst -> Editor -> Auditor -> Formatter
```

## Expected Inputs

Source files, claim ledger entries, or draft markdown as appropriate for the pipeline stage.

## Expected Outputs

Structured artifacts conforming to the workflow contract:
- `draft_brief.md`
- `claim_ledger.json`
- `audit_report.json`
- `source_map.md`
