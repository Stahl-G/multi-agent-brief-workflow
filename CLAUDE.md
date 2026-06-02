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
| Init workspace | `multi-agent-brief init ws --language zh-CN --company "Name" --industry solar --title "Brief" --audience management --source-profile research` |
| Run pipeline | `multi-agent-brief run --config ws/config.yaml` |
| Doctor check | `multi-agent-brief doctor --config ws/config.yaml` |
| Run tests | `python3 -m pytest -q` |
| Demo | `multi-agent-brief init --demo && multi-agent-brief run --config brief-demo/config.yaml` |

### Generate a brief (workflow)

1. `init` workspace if not exists (ask user for company/industry/title/audience)
2. Ensure source files in `ws/input/` (`.md`, `.txt`, `.json`)
3. `run` pipeline → show `ws/output/brief.md`
4. If audit fails → show findings → fix → re-run

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
scripts/       setup.sh, generate_agent_configs.py
tests/         pytest suite
```

### Rules

- Python 3.9+, type hints, dataclasses, ABC
- No network calls in tests
- Generated files have `AUTO-GENERATED` header — edit `configs/agent_roles.yaml`
- No API keys in config — use env var refs
- `user.md` is agent context, never put it in `input/`
