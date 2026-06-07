---
name: screener
description: Screens, ranks, deduplicates, freshness-checks, and capacity-caps candidate claims. Use after scout writes output/intermediate/candidate_claims.json and before creating output/intermediate/screened_candidates.json.
---

# Screener Skill Contract

## Scope

This is a runtime skill contract. It describes the capability and artifact contract for this role.

It is not the platform-specific subagent definition. Claude Code subagents live in `.claude/agents/`; OpenCode subagents live in `.opencode/agents/`; Codex custom agents live in `.codex/agents/`; Hermes child tasks are created through `delegate_task`.

## Purpose

Select the most relevant, fresh, non-duplicative candidates before claim ledger creation.

## Use When

Use after scout has written candidate_claims.json.

## Inputs

- `output/intermediate/candidate_claims.json`
- `config.yaml`
- `user.md`

## Outputs

- `output/intermediate/screened_candidates.json`

## Work

- Rank candidates by relevance, freshness, source quality, and user focus.
- Deduplicate exact and near-duplicate candidates.
- Apply topic capacity and reporting-window rules from config.
- Preserve source identity, evidence text, and exclusion reasons.

## Handoff

Pass screened_candidates.json to claim-ledger.
