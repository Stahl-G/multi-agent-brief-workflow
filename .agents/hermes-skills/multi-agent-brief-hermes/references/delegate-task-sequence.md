# Hermes Delegate Task Sequence

The Hermes parent agent is the Orchestrator main agent. It uses `delegate_task` children for role work and Python CLI tools for setup, validation, and rendering. Each child starts with a fresh context, so include the workspace path, inputs, output artifact path, role goal, and return summary requirements in the child context.

Read these contract references before delegation:

- `configs/orchestrator_contract.yaml`
- `configs/stage_specs.yaml`
- `configs/artifact_contracts.yaml`
- `configs/policy_packs/default.yaml`

Control loop:

```text
Read workspace context -> read contract references -> identify the next stage -> delegate a specialist or Python tool -> check the expected artifact -> decide continue / retry_stage / delegate_repair / request_human_review / block_run / finalize.
```

## Parent Responsibilities

1. Read `config.yaml`, `sources.yaml`, `user.md`, `input/`, and `input/hermes_cache/` when present.
2. Run `multi-agent-brief doctor --config <workspace>/config.yaml`.
3. Run source discovery when configured.
4. Run input governance when available.
5. Create `output/intermediate/` when needed.
6. Delegate child tasks in sequence.
7. Verify each expected artifact exists and is non-empty before selecting the next decision.
8. Decide `continue`, `retry_stage`, `delegate_repair`, `request_human_review`, `block_run`, or `finalize`.
9. Run `multi-agent-brief finalize --config <workspace>/config.yaml` after audit readiness.

## Child Task Templates

### Scout

Goal: Extract candidate reportable items for a MABW brief.

Context should include:

- Workspace path
- Approved evidence inputs, cached source packages, local source files, and source config
- Write path: `output/intermediate/candidate_claims.json`
- Required fields: source path or URL, source date, evidence text, topic, claim type, confidence

Toolsets: `file`, `terminal`, `web` when source access is enabled.

### Screener

Goal: Screen and rank MABW candidate claims.

Input: `output/intermediate/candidate_claims.json`  
Write: `output/intermediate/screened_candidates.json`

Rank, deduplicate, freshness-check, and capacity-cap candidates while preserving source evidence and exclusion reasons.

### Claim Ledger

Goal: Build the MABW Claim Ledger.

Input: `output/intermediate/screened_candidates.json`  
Write: `output/intermediate/claim_ledger.json`

Create stable claim IDs and preserve evidence text, source URL/path, publication date, retrieved date, topic, claim type, and confidence.

### Analyst

Goal: Draft the audited MABW brief.

Inputs: `user.md`, `config.yaml`, `output/intermediate/claim_ledger.json`  
Write: `output/intermediate/audited_brief.md`

Write a management-ready brief in the workspace language with valid `[src:CLAIM_ID]` citations.

### Editor

Goal: Polish the audited MABW brief.

Input and output: `output/intermediate/audited_brief.md`

Improve readability, structure, and executive tone while preserving factual scope, caveats, uncertainty, and valid citations.

### Auditor

Goal: Audit the MABW brief against the Claim Ledger.

Inputs: `output/intermediate/audited_brief.md`, `output/intermediate/claim_ledger.json`  
Write: `output/intermediate/audit_report.json`

Check source support, orphan citations, unsupported numbers, missing dates, stale framing, process residue, advice language, and delivery readiness.
