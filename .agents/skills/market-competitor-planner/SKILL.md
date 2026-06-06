---
name: market-competitor-planner
description: Recommends competitor candidates for a workspace based on user.md context (company, industry, market_scope, focus_areas). Use during workspace setup or when the user runs 'multi-agent-brief competitors propose'. Read user.md and recommend competitors for competitor_candidates.yaml.
---

# Market Competitor Planner Skill

## Purpose

Recommends competitor candidates for a workspace based on user.md context (company, industry, market_scope, focus_areas).

## When To Use

Use during workspace setup or when the user runs 'multi-agent-brief competitors propose'. Read user.md and recommend competitors for competitor_candidates.yaml.

## Responsibilities

- Read user.md (company, industry, market_scope, focus_areas) for context.
- Recommend 3-8 competitor entities based on industry knowledge.
- Write competitor_candidates.yaml with entity_id, name, aliases, relation, relevance_reason, market_overlap.
- Recommend candidates for user review.

## Guardrails

- Write recommendations to competitor_candidates.yaml for review.
- Give every entity a relevance_reason.
- Only use publicly known competitor information.

## Subagent workflow Context

```text
Scout -> Screener -> Claim Ledger -> Analyst -> Editor -> Auditor -> Formatter
```

## Expected Inputs

Source files, claim ledger entries, or draft markdown as appropriate for the analysis_module stage.

## Expected Outputs

Structured artifacts conforming to the workflow contract:
- `draft_brief.md`
- `claim_ledger.json`
- `audit_report.json`
- `source_map.md`
