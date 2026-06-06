---
name: formatter
description: Writes and validates preparation artifacts: draft_brief.md, claim_ledger.json, audit_report.json, source_map.md. Use when implementing or reviewing output file writing, JSON validity, source maps, Markdown/DOCX/PDF rendering contracts.
---

# Formatter Skill

## Purpose

Writes and validates preparation artifacts: draft_brief.md, claim_ledger.json, audit_report.json, source_map.md.

## When To Use

Use when implementing or reviewing output file writing, JSON validity, source maps, Markdown/DOCX/PDF rendering contracts.

## Responsibilities

- Write files only inside configured output directories.
- Validate JSON artifacts.
- Validate cited claim IDs exist.
- Preserve deterministic formatting.

## Guardrails

- Surface failed audits clearly.
- Fix rendering defects without changing substantive content.
- Write files only inside configured output directories.

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
