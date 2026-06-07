# CLAUDE.md

## Claude Code Role

This file is for developing and running Multi-Agent Brief Workflow inside Claude Code.

For runtime-neutral instructions, see `AGENTS.md`. For Claude Code execution, use the repository slash command and subagents.

## Standard Claude Code Path

For a real brief workspace:

```bash
multi-agent-brief onboard
multi-agent-brief init ../mabw-workspace --from-onboarding onboarding.json
```

Then run in Claude Code:

```text
/generate-brief ../mabw-workspace
```

For a demo workspace:

```bash
multi-agent-brief init ../mabw-demo --demo
```

Then run:

```text
/generate-brief ../mabw-demo
```

## Repository Development Setup

```bash
bash scripts/setup.sh
source .venv/bin/activate
python -m pytest -q
```

Windows PowerShell:

```powershell
.\scripts\setup.ps1
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

## Useful Commands

```bash
multi-agent-brief version
multi-agent-brief onboard
multi-agent-brief init ../mabw-workspace --from-onboarding onboarding.json
multi-agent-brief run --workspace ../mabw-workspace --runtime claude
multi-agent-brief doctor --config ../mabw-workspace/config.yaml
multi-agent-brief sources decide --config ../mabw-workspace/config.yaml
multi-agent-brief sources decide --config ../mabw-workspace/config.yaml --merge
multi-agent-brief finalize --config ../mabw-workspace/config.yaml
python scripts/generate_agent_configs.py --check
```

## Context Mode

When the user provides a workspace path, treat that path as the workspace even if the current shell is inside the source repository.

Workspace evidence comes from workspace input files, source configuration, collected provider outputs, and intermediate artifacts. Repository docs, examples, README files, and agent configs are development references.

## Subagent Workflow

Claude Code uses the external subagent workflow:

```text
source-planner
→ scout
→ screener
→ claim-ledger
→ analyst
→ editor
→ auditor
→ formatter/finalize
```

Python CLI commands provide setup, source discovery, input governance, audit checks, runtime handoff, and final rendering tools. The auditable brief is written by subagents and rendered through `finalize`.

## Generated And Hand-Maintained Files

Generated platform adapter files come from:

```text
configs/agent_roles.yaml
scripts/generate_agent_configs.py
```

Generated targets are limited to `.codex/`, `.claude/agents/`, `.opencode/`, and `docs/agents/`.

Hand-maintained operating contracts:

```text
AGENTS.md
CLAUDE.md
.agents/AGENTS.md
.agents/skills/*/SKILL.md
.agents/hermes-skills/*
```

Do not regenerate hand-maintained operating contracts from `configs/agent_roles.yaml`.

## Focused Tests

For launcher and runtime handoff changes:

```bash
python -m pytest tests/test_start_commands.py tests/test_hermes_adapter.py tests/test_agent_config_generation.py -q
```

For onboarding changes:

```bash
python -m pytest tests/test_onboarding*.py tests/test_init*.py -q
```

For skill contract changes:

```bash
python -m pytest tests/test_skill_contracts.py -q
```

For final validation:

```bash
python -m pytest -q
```

## Development Governance

Prefer deletion and simplification over new abstraction.

Python CLI is harness/tooling, not the brief-generation runtime. Do not add a Python full-run pipeline, `BriefPipeline`, `prepare` runtime, or a new full-run generator.

`main.py` should remain a thin CLI router. Command behavior belongs in command modules.

`AGENTS.md` and `SKILL.md` files are operating contracts. Keep them short, concrete, and positive. Use frontmatter descriptions for routing and `references/` for long material.

When documenting agent behavior, describe the active path first: inputs, action, output, handoff. Place deprecated paths and failure cases in tests, validators, or legacy stubs rather than in runtime-facing prompt text.

If an issue is already fixed, report the evidence and stop instead of making unnecessary changes.

Before final response, report files changed, tests run, and known risks.
