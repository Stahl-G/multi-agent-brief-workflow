---
name: multi-agent-brief-hermes
description: Run Multi-Agent Brief Workflow workspaces from Hermes cron, collecting daily source packages and triggering audited weekly/monthly briefs.
version: 0.5.5
author: multi-agent-brief-workflow
license: MIT
platforms:
  - linux
  - macos
  - windows
tags:
  - hermes
  - cron
  - brief
  - research
  - workflow
---

# Multi-Agent Brief Workflow for Hermes

Use this skill when a Hermes cron job needs to collect daily signals for a MABW workspace or trigger an audited weekly/monthly brief.

## Operating Model

Hermes provides scheduled execution, daily source collection, cache preparation, and delivery notifications. Formal brief generation follows the MABW subagent workflow:

```text
scout -> screener -> claim-ledger -> analyst -> editor -> auditor -> formatter
```

If you already use Claude Code, the recommended formal generation path is:

```text
/generate-brief <workspace>
```

Claude Code can invoke the project's full subagent workflow. Hermes remains useful for scheduled source collection, cache preparation, reminders, and delivery notifications.

## Daily Scout Workflow

1. Read the cron prompt for the absolute workspace path and cache directory.
2. Collect public, citable source signals relevant to the configured company, industry/theme, audience, and report language.
3. Write one JSON file under the cache directory named `YYYY-MM-DD.json`.
4. Use this item shape when possible:

```json
{
  "source_id": "HERMES_YYYYMMDD_001",
  "source_name": "Source name",
  "source_type": "hermes_daily_cache",
  "title": "Short source title",
  "content": "Concise factual summary with enough context for claim extraction.",
  "url": "https://example.com/source",
  "published_at": "YYYY-MM-DD",
  "reliability": "high",
  "metadata": {
    "collected_by": "hermes",
    "collection_cadence": "daily"
  }
}
```

5. End with a short count of saved usable items and any source gaps.

## Weekly / Monthly Brief Workflow

1. Confirm the workspace has `config.yaml`, `sources.yaml`, and `user.md`.
2. Ensure `sources.yaml` enables required source providers, including `cached_package` for `input/hermes_cache` when daily Hermes scout cache is used.
3. Run doctor:

```bash
multi-agent-brief doctor --config <workspace>/config.yaml
```

4. Generate the brief through the subagent workflow:
   - Recommended for Claude Code users: `/generate-brief <workspace>`.
   - Hermes-native continuation: use scout, screener, claim-ledger, analyst, editor, and auditor roles in that order.
5. After `output/intermediate/audited_brief.md` exists, run finalize:

```bash
multi-agent-brief finalize --config <workspace>/config.yaml
```

6. Report artifact paths for:
   - `output/brief.md`
   - named Markdown if configured
   - `output/brief.docx` if configured
   - `output/intermediate/audited_brief.md`
   - `output/intermediate/claim_ledger.json`
   - `output/intermediate/audit_report.json`

## Source Cache Contract

The MABW `cached_package` provider can read JSON, Markdown, and text files from the configured cache directory. Prefer JSON arrays or objects with an `items` array. Each item should preserve URL, publication date, source name, and reliability where available.

## Hermes Cron Notes

- Attach this skill to each cron job with `--skill multi-agent-brief-hermes`.
- Use `--workdir <repo-root>` so Hermes loads repository instructions and runs commands from the project.
- Pin `--profile <name>` when the Hermes profile already exists.
- Hermes delivers the final response through the configured cron destination.
