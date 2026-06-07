---
name: market-competitor-analyst
description: Generates competitor analysis cards from an evidence pack. Use after competitor evidence has been collected and write competitor sections for the final brief.
---

# Market Competitor Analyst Skill Contract

## Scope

This is a runtime skill contract. It describes the capability and artifact contract for this role.

It is not the platform-specific subagent definition. Claude Code subagents live in `.claude/agents/`; OpenCode subagents live in `.opencode/agents/`; Codex custom agents live in `.codex/agents/`; Hermes child tasks are created through `delegate_task`.

## Purpose

Generate competitor analysis from evidence packs.

## Use When

Use when evidence_pack.json or equivalent competitor evidence is available.

## Inputs

- `evidence_pack.json`
- competitor candidates
- claim ledger entries when available

## Outputs

- competitor AnalysisCards
- competitor section draft or analysis module output

## Work

- Compare competitors using sourced evidence.
- Preserve metric basis, dates, source quality, and uncertainty.
- Separate observed facts from analytical interpretation.

## Handoff

Pass competitor analysis output to market-competitor-auditor or analyst.
