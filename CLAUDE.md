# CLAUDE.md

@AGENTS.md

## Claude Code

### Setup (first after clone)

```bash
bash scripts/setup.sh && source .venv/bin/activate
```

Windows (PowerShell):

```powershell
.\scripts\setup.ps1; .\.venv\Scripts\Activate.ps1
```

### Commands

| Task | Command |
|------|---------|
| Init workspace | `multi-agent-brief init ws --language zh-CN --company "Name" --industry finance --title "Brief" --audience management --source-profile research` |
| Run pipeline | `multi-agent-brief run --config ws/config.yaml` |
| Doctor check | `multi-agent-brief doctor --config ws/config.yaml` |
| Run tests | `python3 -m pytest -q` |

### Init: interactive vs non-interactive

**`multi-agent-brief init` (no args)** → enters interactive wizard with 13 prompts. The agent must STOP and let the user answer each question. Do NOT pre-fill answers.

**`multi-agent-brief init ws --language zh-CN --company "Name" --industry finance --title "..." --audience management --source-profile research`** → non-interactive, uses CLI args. Agent can run this directly without asking user.

**Important:** If you pass even ONE arg (like `--language`), the entire interactive wizard is SKIPPED. So either pass ALL args or pass NONE.

### Generate a brief (workflow)

1. Ask user: company, industry, title, audience (if not using interactive init)
2. `init` workspace
3. Ensure source files in `ws/input/` (`.md`, `.txt`, `.json`)
4. `run` pipeline → show `ws/output/brief.md`
5. If audit fails → show findings → fix → re-run

### Source profiles

- `conservative` — official only
- `research` — official + industry + RSS (default)
- `aggressive_signal` — broad signals, more noise
- `custom` — user edits sources.yaml
- `llm_decide` — agent-readable discovery policy, no LLM at init

### Layout

```text
src/multi_agent_brief/
  cli/         main.py, init_wizard.py
  core/        pipeline, config, schemas, claim ledger
  agents/      Scout, Screener, Analyst, Auditor, Editor, Formatter
  audit/       deterministic, quality harness, final quality
  sources/     providers, registry, doctor
configs/       agent_roles.yaml (source of truth)
scripts/       setup.sh, setup.ps1, generate_agent_configs.py
tests/         pytest suite
```

### Rules

- Python 3.9+, type hints, dataclasses, ABC
- No network calls in tests
- Generated files have `AUTO-GENERATED` header — edit `configs/agent_roles.yaml`
- No API keys in config — use env var refs
- `user.md` is agent context, never put it in `input/`
