# AGENTS.md

## Purpose

Multi-Agent Brief Workflow is a subagent-first briefing toolkit.

Python CLI commands provide onboarding, workspace setup, runtime handoff, source tooling, validation, audit checks, and final rendering. The selected agent runtime coordinates the brief workflow through handoff artifacts and role-specific agents.

## Instruction Scope

This repository contains both development code and runtime agent contracts.

In repository development mode, files under `.agents/skills/`, `.agents/hermes-skills/`, `.claude/agents/`, `.codex/agents/`, and `.opencode/agents/` are source assets to inspect, edit, and test. Their role instructions become active only when the corresponding runtime explicitly invokes that role or skill.

Use `multi-agent-brief run --workspace <workspace>` to create a runtime handoff. The handoff artifact, not this repository manual, is the execution contract for a specific brief run.

## Context Mode

### Repository development mode

If the current directory contains `pyproject.toml`, `src/`, `tests/`, or `scripts/`, treat it as the source repository.

Use repository files for development, debugging, tests, generated configs, and documentation updates.

### Generated workspace mode

If the current directory contains `config.yaml`, `sources.yaml`, `user.md`, and `input/`, treat it as an end-user brief workspace.

Use workspace files as task context. Treat repository README, examples, agent configs, and docs as references, not source evidence.

## Standard User Path

For a real brief workspace:

```bash
multi-agent-brief onboard
multi-agent-brief init <workspace> --from-onboarding onboarding.json
multi-agent-brief run --workspace <workspace>
```

For demo exploration:

```bash
multi-agent-brief init <workspace> --demo
multi-agent-brief run --workspace <workspace>
```

`run` is the standard user-facing runtime handoff launcher. Hermes is the default runtime unless another runtime is selected.

## Runtime Handoff

Supported runtimes:

- `hermes`: Hermes parent agent uses `delegate_task` children.
- `claude`: Claude Code uses the repository command workflow.
- `opencode`: OpenCode uses the repository command and agent files.
- `codex`: Codex uses repository agent instructions and generated configs.
- `manual`: prints the artifact workflow.

Canonical workflow:

```text
doctor
→ source discovery when configured
→ input governance when available
→ scout
→ screener
→ claim-ledger
→ analyst
→ editor
→ auditor
→ finalize
```

## Onboarding

Use `multi-agent-brief onboard` for requirement capture. It collects company or organization, industry or theme, task objective, audience, language, cadence, source style, output style, must-watch topics, excluded topics, and source/search preference.

For details, see `docs/onboarding.md`.

## Role Details

- `.agents/skills/*/SKILL.md` — runtime capability contracts, hand-maintained.
- `.agents/hermes-skills/*/SKILL.md` — Hermes runtime skills and reference files, hand-maintained.
- `.claude/agents/*.md` — Claude Code subagent definitions.
- `.codex/agents/*.toml` — Codex custom agent configs.
- `.opencode/agents/*.md` — OpenCode subagent definitions.
- `docs/agents/` — generated platform adapter documentation.

## Artifact Contract

Expected workflow artifacts:

```text
output/intermediate/candidate_claims.json
output/intermediate/screened_candidates.json
output/intermediate/claim_ledger.json
output/intermediate/audited_brief.md
output/intermediate/audit_report.json
output/brief.md
```

Detailed schemas, delivery gates, and harness rules belong in tests, validators, audit rules, and docs.
