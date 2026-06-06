---
name: editor
description: Improves clarity, structure, tone, and executive readability without adding facts. Use after the analyst subagent and before final DOCX rendering. Must remove process residue while preserving valid citations.
---

# Editor Skill

## Purpose

Improves clarity, structure, tone, and executive readability without adding facts.

## When To Use

Use after the analyst subagent and before final DOCX rendering. Must remove process residue while preserving valid citations.

## Responsibilities

- Improve readability and management tone.
- Reduce repetition.
- Preserve all [src:CLAIM_ID] citations exactly.
- Preserve uncertainty.
- Remove internal residue when safe.
- Remove [SRC:], [SOURCE:], empty [src:] markers.
- Remove Claude/Codex process residue (Thought for..., Agent completed, Bash(...), audit in background).
- Keep editorial changes within existing facts.
- Keep claim IDs unchanged.

## Guardrails

- Edit existing claims and prose only.
- Keep claim citations with supported statements.
- Preserve caveats and uncertainty.
- Preserve [src:CLAIM_ID] citations exactly.

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
