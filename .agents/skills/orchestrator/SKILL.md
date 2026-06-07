---
name: orchestrator
description: Coordinates MABW runtime handoff and artifact sequencing across roles. Use for multi-step workflow coordination, runtime integration, generated adapter updates, or cross-role changes.
---

# Orchestrator Skill Contract

## Scope

This is a runtime skill contract. It describes the capability and artifact contract for this role.

It is not the platform-specific subagent definition. Claude Code subagents live in `.claude/agents/`; OpenCode subagents live in `.opencode/agents/`; Codex custom agents live in `.codex/agents/`; Hermes child tasks are created through `delegate_task`.

## Purpose

Coordinate runtime handoff and role sequencing across MABW workflows.

## Use When

Use for multi-step workflow coordination, runtime integration, generated adapter config updates, or cross-role changes.

## Inputs

- workspace path
- runtime handoff artifact
- `config.yaml`
- `sources.yaml`
- `user.md`
- intermediate artifact status

## Outputs

- workflow plan
- runtime handoff updates
- implementation checklist
- test plan

## Work

- Use multi-agent-brief run --workspace <workspace> as the standard launcher.
- Keep role handoffs artifact-based.
- Coordinate source-planner, scout, screener, claim-ledger, analyst, editor, auditor, and formatter.
- Update generation sources when generated platform adapter files change.
- Run focused tests for changed areas.

## Handoff

Return the next role, expected artifact, and validation command.
