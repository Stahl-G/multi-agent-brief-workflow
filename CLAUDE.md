# CLAUDE.md

@AGENTS.md

## Claude Code

### Setup

```bash
bash scripts/setup.sh && source .venv/bin/activate
```

### Commands

| Task | Command |
|------|---------|
| Init workspace | `multi-agent-brief init ../mabw-workspace --from-onboarding onboarding.json` |
| Generate brief | `/generate-brief ../mabw-workspace` |
| Doctor check | `multi-agent-brief doctor --config ../mabw-workspace/config.yaml` |
| Source decide | `multi-agent-brief sources decide --config ../mabw-workspace/config.yaml` |
| Merge sources | `multi-agent-brief sources decide --config ../mabw-workspace/config.yaml --merge` |
| Finalize reader artifacts | `multi-agent-brief finalize --config ../mabw-workspace/config.yaml` |
| Run tests | `python -m pytest -q` |
| Agent config check | `python scripts/generate_agent_configs.py --check` |

## Context Mode Rule

When a user request or command provides a workspace path, classify that path as the workspace, even if the current working directory is the source repo.

Example: if you are in `/path/to/repo/` and the user says "generate a brief for ../mabw-workspace", the workspace is `../mabw-workspace`.

Workspace evidence comes from the workspace input/source configuration and collected provider outputs. Repo README, docs, examples, and agent files are development references.

## Conversational Onboarding Policy

When the user asks to initialize, start, or configure a brief workspace:

1. Ask plain-language questions directly in chat.
2. Cover all onboarding fields: company, industry, task, audience, language, cadence, source style, output style, must-watch topics, excluded sources/topics, and web-search configuration.
3. Let the user answer naturally in one message.
4. Confirm required fields and defaults explicitly.
5. Convert answers internally to `onboarding.json`.
6. Run `multi-agent-brief init <workspace> --from-onboarding onboarding.json`.
7. Use AskUserQuestion for optional single-choice refinements.
8. Keep YAML, schema, source_profile, selector_max_items, retrieval_provider, output_formats, and CLI flags in developer-facing explanations unless the user asks for them.

## Subagent Runtime

MABW uses the external subagent workflow for real brief generation:

```text
source-planner → scout → screener → claim-ledger → analyst → editor → auditor → formatter
```

Python commands provide setup, source discovery, input governance, audit checks, and final rendering tools. The auditable brief is produced by subagents and rendered with `finalize`.

## Source Profiles

- `conservative` — official only
- `research` — official + industry + RSS
- `aggressive_signal` — broad signals, more noise
- `custom` — user edits sources.yaml
- `llm_decide` — agent-readable discovery policy, no LLM at init (default)

## Layout

```text
src/multi_agent_brief/
  cli/         CLI commands and init wizard
  core/        config, schemas, claim ledger
  audit/       deterministic checks, harnesses, final quality
  sources/     providers, registry, doctor
  outputs/     finalize and rendering helpers
configs/       agent_roles.yaml (source of truth)
scripts/       setup.sh, setup.ps1, generate_agent_configs.py
tests/         pytest suite
```

## Development Guardrails

- Python 3.9+, type hints, dataclasses, ABC
- Windows native path is PowerShell: `.\scripts\setup.ps1`, `.\.venv\Scripts\Activate.ps1`, `python -m pytest -q`
- WSL is optional
- Tests use deterministic fixtures
- Generated files have `AUTO-GENERATED` header; edit `configs/agent_roles.yaml`
- API keys use env var refs
- `user.md` is agent context; source evidence lives in workspace input/source configuration
