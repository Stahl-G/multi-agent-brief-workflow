# Claude Code Agent Workflow

## Architecture

MABW uses a subagent-first workflow. Python CLI commands provide setup, source discovery, input governance, audit checks, and final rendering. Subagents produce the actual brief.

```text
multi-agent-brief init → /generate-brief (Claude Code) → output artifacts
```

### CLI Tools

- `multi-agent-brief init` — create workspace
- `multi-agent-brief doctor` — check configuration health
- `multi-agent-brief sources decide` — resolve llm_decide source policy
- `multi-agent-brief inputs classify` — classify inputs as evidence/non-evidence
- `multi-agent-brief finalize` — render reader-facing Markdown/DOCX from audited_brief.md
- `multi-agent-brief audit` — run deterministic audit checks

### Subagent Workflow

```text
scout → screener → claim-ledger → analyst → editor → auditor → finalize
```

- **Subagent definitions**: `.claude/agents/*.md` (Markdown + YAML frontmatter)
- **Interactive orchestration**: Claude Code spawns subagents as needed
- **Model-assisted judgment**: subagents use LLM for extraction, analysis, editing
- **Source grounding**: all subagents respect Claim Ledger and citation contracts
- **No SDK dependency**: subagents are pure Markdown prompts, not Python code

## How The Workflow Executes

```text
┌─────────────────────────────────────────────────────┐
│  Claude Code Session                                │
│                                                     │
│  User: "Generate a weekly brief for my company"     │
│         │                                           │
│         ▼                                           │
│  source discovery (if llm_decide)                   │
│    → sources decide + merge                         │
│         │                                           │
│         ▼                                           │
│  doctor gate                                        │
│    → fix config issues                              │
│         │                                           │
│         ▼                                           │
│  scout subagent                                     │
│    → reads sources, extracts candidates             │
│    → writes candidate_claims.json                   │
│         │                                           │
│         ▼                                           │
│  screener subagent                                  │
│    → dedupe, rank, freshness-check                  │
│    → writes screened_candidates.json                │
│         │                                           │
│         ▼                                           │
│  claim-ledger subagent                              │
│    → converts to source-grounded claims             │
│    → writes claim_ledger.json                       │
│         │                                           │
│         ▼                                           │
│  analyst subagent                                   │
│    → reads claim_ledger.json and user.md            │
│    → writes audited_brief.md                        │
│    → preserves all [src:CLAIM_ID] citations         │
│         │                                           │
│         ▼                                           │
│  editor subagent                                    │
│    → improves readability and management tone       │
│    → preserves all citations                        │
│         │                                           │
│         ▼                                           │
│  auditor subagent                                   │
│    → reviews audited_brief.md against ledger        │
│    → reports findings and recommends fixes          │
│         │                                           │
│         ▼                                           │
│  finalize                                           │
│    → strips [src:CLAIM_ID] for brief.md             │
│    → generates DOCX if configured                   │
└─────────────────────────────────────────────────────┘
```

## Available Subagents

| Subagent | Role | Purpose |
|----------|------|---------|
| `source-planner` | coordination | Generate/refine source_candidates.yaml and search_tasks |
| `source-provider` | coordination | Configure and collect sources from providers |
| `scout` | pipeline | Extract candidate reportable items from sources |
| `screener` | pipeline | Filter, rank, deduplicate candidates |
| `claim-ledger` | pipeline | Convert candidates to source-grounded claims |
| `analyst` | pipeline | Draft management-ready brief sections |
| `editor` | pipeline | Improve readability without adding facts |
| `auditor` | pipeline | Review final brief against ledger and audit report |
| `formatter` | pipeline | Write final output artifacts |
| `orchestrator` | coordination | Coordinate multi-step work |
| `draft-audit-harness` | harness | Draft-level audit checks |
| `final-quality-harness` | harness | Final text quality gates |
| `rendered-output-harness` | harness | DOCX/PDF rendering fidelity checks |

## Key Design Decisions

### Why Subagent-First?

1. **Testability**: CLI tools have 100+ tests covering setup, source discovery, audit, and finalize. Subagent behavior is validated through audit gates.
2. **Flexibility**: Subagents can adapt to different workspace configurations, languages, and audience profiles.
3. **Auditability**: Deterministic audit gates in Python are repeatable. Model-assisted checks are complementary.
4. **No SDK lock-in**: Subagents are pure Markdown — no Anthropic SDK dependency in the Python package.

### What Stays in Python CLI

- Workspace initialization and configuration
- Source discovery and provider management
- Input governance and classification
- Deterministic audit checks
- Final rendering (finalize)

### What Stays in Subagents

- Source scouting and candidate extraction
- Screening and deduplication
- Claim ledger construction
- Brief section drafting
- Prose editing and readability improvement
- Final review and recommendation

## Usage Patterns

### Pattern 1: Full Agent Workflow

```text
1. User asks Claude Code to generate a brief
2. CLI resolves sources and checks config
3. Subagents produce the brief through scout → screener → claim-ledger → analyst → editor → auditor
4. CLI finalizes reader-facing output
```

### Pattern 2: Hybrid

```text
1. User runs multi-agent-brief init (CLI)
2. User asks Claude Code source-planner to refine sources
3. User runs /generate-brief in Claude Code
4. User asks Claude Code auditor to review output
```

## See Also

- [docs/claude-code-quickstart.md](claude-code-quickstart.md) — Command guide with sample prompts
- [docs/agents/claude-code.md](agents/claude-code.md) — Subagent configuration reference
- [docs/architecture.md](architecture.md) — Architecture overview
- [docs/harness.md](harness.md) — Audit harness design
