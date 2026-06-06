---
name: market-competitor-auditor
description: Runs 6 specialist audits on competitor analysis output: comparison evidence, capacity status, metric basis, market trends, single-source confidence, and coverage gaps. Use after analysis_cards.json is generated. Validate against claim_ledger.json and competitors.json.
---

# Market Competitor Auditor Skill

## Purpose

Runs 6 specialist audits on competitor analysis output: comparison evidence, capacity status, metric basis, market trends, single-source confidence, and coverage gaps.

## When To Use

Use after analysis_cards.json is generated. Validate against claim_ledger.json and competitors.json.

## Responsibilities

- Check comparison claims have evidence for each entity cited.
- Check capacity events have a status (announced vs operational vs etc).
- Check numeric values have period and unit in supporting claims.
- Check market trend claims have at least 2 supporting claims.
- Check single-source interpretations use confidence='low'.
- Check primary competitors all have coverage.
- Update audit_report.json with MC-specific findings.

## Guardrails

- Preserve audit gates while fixing failures.
- Treat model judgment as analysis, not source evidence.
- Treat announced capacity as announced until operational evidence exists.

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
