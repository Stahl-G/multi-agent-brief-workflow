---
name: source-provider
description: Configures, validates, collects, and normalizes source provider outputs. Use when working on sources.yaml, provider configuration, cached packages, source collection, or doctor findings.
---

# Source Provider Skill Contract

## Scope

This is a runtime skill contract. It describes the capability and artifact contract for this role.

It is not the platform-specific subagent definition. Claude Code subagents live in `.claude/agents/`; OpenCode subagents live in `.opencode/agents/`; Codex custom agents live in `.codex/agents/`; Hermes child tasks are created through `delegate_task`.

## Purpose

Configure, validate, collect, and normalize source provider outputs.

## Use When

Use when working on sources.yaml, provider configuration, source collection, cached packages, or doctor checks.

## Inputs

- `sources.yaml`
- `config.yaml`
- provider outputs
- `input/`
- `input/hermes_cache/`

## Outputs

- normalized source packages
- doctor report
- provider validation findings
- cached package source configuration when applicable

## Work

- Validate enabled providers and source configuration.
- Normalize collected source items.
- Deduplicate and label collected items.
- Surface provider configuration and collection issues clearly.

## Handoff

Pass normalized evidence material to scout.
