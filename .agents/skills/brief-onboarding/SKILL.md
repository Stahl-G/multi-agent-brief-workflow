---
name: brief-onboarding
description: Captures brief requirements and creates onboarding.json for workspace initialization. Use when a user wants to set up a real MABW workspace before init --from-onboarding.
---

# Brief Onboarding Skill Contract

## Scope

This is a runtime skill contract. It describes the capability and artifact contract for this role.

It is not the platform-specific subagent definition. Claude Code subagents live in `.claude/agents/`; OpenCode subagents live in `.opencode/agents/`; Codex custom agents live in `.codex/agents/`; Hermes child tasks are created through `delegate_task`.

## Purpose

Capture business requirements to initialize, start, configure, and set up a real brief workspace.

## Use When

Use before workspace creation when company, topic, audience, language, cadence, source preference, or output style are not yet defined.

## Inputs

- user answers in natural language
- optional existing onboarding.json for review

## Outputs

- `onboarding.json`

## Work

- Collect company or organization, industry or theme, task objective, audience, language, cadence, source style, output style, must-watch topics, exclusions, and source/search preference.
- Confirm required values before workspace creation.
- Write onboarding.json in the schema expected by multi-agent-brief init --from-onboarding.
- Explain setup in business language.

## Handoff

Run multi-agent-brief init <workspace> --from-onboarding onboarding.json, then multi-agent-brief run --workspace <workspace>.
