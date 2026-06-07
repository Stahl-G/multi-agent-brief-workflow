---
name: multi-agent-brief-hermes
description: Runs Multi-Agent Brief Workflow workspaces inside Hermes using delegate_task child agents, source cache, cron scheduling, and final rendering. Use when the user asks Hermes to generate, schedule, continue, or inspect a MABW brief from a workspace.
license: MIT
compatibility: Requires Hermes with delegate_task support plus terminal and file access to a workspace with the multi-agent-brief CLI installed.
metadata:
  author: multi-agent-brief-workflow
  version: 0.5.6
  tags:
    - hermes
    - cron
    - brief
    - research
    - delegate-task
---

# Multi-Agent Brief Workflow for Hermes

## Scope

This skill is the Hermes runtime contract for MABW. It applies when Hermes is asked to set up, schedule, or run a MABW workspace.

Hermes is a native runtime: the Hermes parent agent orchestrates the run and uses `delegate_task` children for role work. Python CLI commands provide setup, validation, source tooling, final rendering, and audit support.

## Use When

Use this skill when the user asks Hermes to:

- create or continue a MABW brief workspace
- generate a management, market, policy, competitor, or research brief
- schedule daily source cache collection or weekly/monthly brief generation
- run the MABW workflow inside Hermes rather than Claude Code

## Hermes Onboarding Workflow

When the user wants to initialize a real MABW workspace in Hermes, run onboarding as a chat-to-JSON workflow.

### Step 1: Collect brief profile in chat

Ask for these fields in plain language:

- company or organization
- industry or theme
- task objective or brief title
- audience
- language
- cadence: daily, weekly, or monthly
- source style: official only, reliable research, or broad scan
- output style
- must-watch topics or entities
- excluded sources or topics
- source/search mode: local input, runtime web search, external API, or configure later

Accept natural-language answers and apply sensible defaults after confirming them.

### Step 2: Write onboarding.json

Create `onboarding.json` in the repository or chosen setup directory.

Use this shape:

```json
{
  "company_or_org": "阿特斯",
  "industry_or_theme": "光伏和储能",
  "task_objective": "美国光储行业简报",
  "audience_plain": "management team",
  "language_plain": "中文",
  "cadence_plain": "weekly",
  "source_style_plain": "reliable research",
  "output_style_plain": "executive brief, conclusion-first",
  "must_watch": [],
  "forbidden_sources": [],
  "search_backend_plain": "runtime_websearch"
}
```

### Step 3: Create the workspace

```bash
multi-agent-brief init <workspace> --from-onboarding onboarding.json
```

### Step 4: Create runtime handoff

```bash
multi-agent-brief run --workspace <workspace>
```

This writes:

```text
<workspace>/output/intermediate/agent_handoff.md
<workspace>/output/intermediate/agent_handoff.json
```

### Step 5: Continue the delegated workflow

Read `agent_handoff.md` and continue inside Hermes as the parent agent.

Use `delegate_task` children for:

```text
scout → screener → claim-ledger → analyst → editor → auditor → finalize
```

After each child returns, check the expected artifact path before starting the next step.

## Existing Workspace Path

For a workspace that already has `config.yaml`:

```bash
multi-agent-brief doctor --config <workspace>/config.yaml
multi-agent-brief hermes prompt --config <workspace>/config.yaml
```

After setup, report repository path, virtual environment path, workspace path, version, and doctor status. Offer to continue in Hermes using delegated child tasks.

## Delegated Brief Run

Parent orchestration sequence:

```text
doctor
→ source discovery when configured
→ input governance when available
→ delegate_task scout
→ delegate_task screener
→ delegate_task claim-ledger
→ delegate_task analyst
→ delegate_task editor
→ delegate_task auditor
→ finalize
```

Read `references/delegate-task-sequence.md` before creating child tasks. Each child task needs complete context, explicit inputs, expected output path, and return summary requirements.

## Daily Source Cache

Daily cache mode collects source signals and writes cache files without drafting a final brief.

Read `references/source-cache-contract.md` before writing cache files.

## Cron Scheduling

Use cron for durable scheduling and `delegate_task` for per-run child work.

Read `references/cron-patterns.md` before creating or editing Hermes cron jobs.

## Reporting

After a delegated run, report:

- `output/brief.md`
- configured named Markdown copy when enabled
- `output/brief.docx` when configured
- `output/intermediate/audited_brief.md`
- `output/intermediate/claim_ledger.json`
- `output/intermediate/audit_report.json`
- audit status and remaining limitations
