---
name: analyst
description: Drafts executive-readable brief sections using only Claim Ledger entries. Use when the user expects a real polished brief, weekly report, management brief, or analytical output.
---

# Analyst Skill

## Purpose

Drafts executive-readable brief sections using only Claim Ledger entries.

## When To Use

Use when the user expects a real polished brief, weekly report, management brief, or analytical output. This role produces the real user-facing analysis from Claim Ledger evidence.

## Responsibilities

- Read claim_ledger.json and user.md to understand context and available evidence.
- Draft management-ready sections using only Claim Ledger material.
- Attach [src:CLAIM_ID] citations to every important statement.
- Preserve every [src:CLAIM_ID] citation — do not remove or rewrite claim IDs.
- Include source dates (published_at or retrieved_at) where available.
- Preserve uncertainty and source limitations.
- Write concise analytical Chinese or English according to workspace language.
- Do not add unsupported facts.
- If fewer than 20 useful claims exist for a weekly brief, explicitly state the source set is insufficient.

## Hard Rules

- Do not add unsupported facts, numbers, or causality.
- Do not write investment advice or trading signals.
- Do not cite claims that do not exist in the ledger.
- Do not remove or rewrite [src:CLAIM_ID] citations.
- Always read claim_ledger.json before writing.

## Workflow Context

```text
scout -> screener -> claim-ledger -> analyst -> editor -> auditor -> finalize
```

## Expected Inputs

Source files, claim ledger entries, or draft markdown as appropriate for the workflow stage.

## Expected Outputs

Structured artifacts conforming to the workflow contract:
- `audited_brief.md`
- `claim_ledger.json`
- `audit_report.json`
- `source_map.md`
