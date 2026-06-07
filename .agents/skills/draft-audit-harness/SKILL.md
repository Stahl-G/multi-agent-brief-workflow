---
name: draft-audit-harness
description: Reviews draft-level audit harness behavior for claim support and citation quality. Use when changing deterministic or semantic draft audit gates and update tests or audit reports.
---

# Draft Audit Harness Skill Contract

## Scope

This is a runtime skill contract. It describes the capability and artifact contract for this role.

It is not the platform-specific subagent definition. Claude Code subagents live in `.claude/agents/`; OpenCode subagents live in `.opencode/agents/`; Codex custom agents live in `.codex/agents/`; Hermes child tasks are created through `delegate_task`.

## Purpose

Review and implement draft-level audit harness behavior.

## Use When

Use when changing audit logic for citations, source support, numbers, source dates, placeholders, confidence leakage, or process residue.

## Inputs

- `output/intermediate/audited_brief.md`
- `output/intermediate/claim_ledger.json`
- audit rule code or tests

## Outputs

- audit findings
- updated audit rules or tests when requested

## Work

- Check citation coverage, orphan claim IDs, unsupported numbers, stale wording, and low-confidence leakage.
- Map each finding to a concrete rule or test.
- Keep deterministic gates in code and regression tests rather than prompt text.

## Handoff

Return rule/test changes and remaining audit risks.
