---
name: market-competitor-auditor
description: Audits competitor analysis for evidence quality and comparison validity. Use after market competitor analysis cards or sections are generated.
---

# Market Competitor Auditor Skill Contract

## Scope

This is a runtime skill contract. It describes the capability and artifact contract for this role.

It is not the platform-specific subagent definition. Claude Code subagents live in `.claude/agents/`; OpenCode subagents live in `.opencode/agents/`; Codex custom agents live in `.codex/agents/`; Hermes child tasks are created through `delegate_task`.

## Purpose

Audit competitor analysis output.

## Use When

Use after competitor analysis cards or sections have been generated.

## Inputs

- competitor analysis output
- `evidence_pack.json`
- claim ledger entries when available

## Outputs

- competitor audit findings
- coverage gaps and confidence notes

## Work

- Check comparison evidence, capacity status, metric basis, market trends, single-source confidence, and coverage gaps.
- Flag unsupported comparisons or stale framing.
- Return blocking findings before final brief integration.

## Handoff

Return competitor audit status and recommended fixes.
