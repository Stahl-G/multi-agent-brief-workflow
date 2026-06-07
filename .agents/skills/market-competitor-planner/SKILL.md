---
name: market-competitor-planner
description: Plans competitor candidates for market competitor analysis. Use when a workspace needs competitor candidates before evidence-pack creation.
---

# Market Competitor Planner Skill Contract

## Scope

This is a runtime skill contract. It describes the capability and artifact contract for this role.

It is not the platform-specific subagent definition. Claude Code subagents live in `.claude/agents/`; OpenCode subagents live in `.opencode/agents/`; Codex custom agents live in `.codex/agents/`; Hermes child tasks are created through `delegate_task`.

## Purpose

Recommend competitor candidates for a workspace.

## Use When

Use when market competitor analysis is enabled and competitor candidates need to be selected or reviewed.

## Inputs

- `user.md`
- `config.yaml`
- market scope
- focus areas

## Outputs

- competitor candidates
- competitor planning notes

## Work

- Identify relevant competitors from company, industry, market scope, and focus areas.
- Separate direct competitors from adjacent players.
- Record rationale and coverage gaps.

## Handoff

Pass competitor candidates to market-competitor-analyst.
