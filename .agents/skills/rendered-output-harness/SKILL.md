---
name: rendered-output-harness
description: Reviews rendered output gates for DOCX/PDF/Markdown rendering fidelity. Use when working on rendered document validation, DOCX text depth, heading mapping, margins, footer fields, or wide table conversion.
---

# Rendered Output Harness Skill

## Purpose

Reviews rendered output gates for DOCX/PDF/Markdown rendering fidelity.

## When To Use

Use when working on rendered document validation, DOCX text depth, heading mapping, margins, footer fields, or wide table conversion.

## Responsibilities

- Validate rendered text depth.
- Validate heading mapping.
- Validate bullet separation after rendering.
- Validate wide table conversion.
- Validate DOCX/PDF dependency behavior.
- Keep renderer-level checks separate from prompt instructions.

## Guardrails

- Fix rendering defects at the rendering layer.
- Report missing rendering dependencies explicitly.
- Use deterministic rendering checks for output validation.

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
