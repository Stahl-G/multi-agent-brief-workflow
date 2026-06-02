# Roadmap

This roadmap keeps the repository focused on a public-safe, local-first MVP while leaving space for richer briefing workflows.

## MVP Completed

- Local `.md`, `.txt`, and `.json` input loading
- Scout agent for candidate item extraction
- Claim Ledger with traceable source-backed claims
- Analyst draft with `[src:CLAIM_ID]` citations
- Deterministic audit for missing claims, unsupported numbers, duplicate claims, redaction risk, and stale source checks
- Quality harness checks for placeholders, process residue, low-confidence sources, stale filler, and unit risk
- Markdown brief, claim ledger, audit report, and source map outputs
- Basic CLI and pytest coverage

## Near-Term

- Add DOCX and PDF output implementations with synthetic examples
- Implement SEC and RSS connectors behind public interfaces
- Add a model-backed semantic audit adapter
- Expand public-safe examples, including peer-review and policy-brief demos
- Improve README, architecture, and harness documentation
- Add repository metadata guidance for GitHub description and topics

## Mid-Term

- Add industry modules for repeatable brief structures
- Add role modules for management, analyst, IR, strategy, and policy audiences
- Add external analysis plugins that must write through the Claim Ledger
- Add local corpus retrieval while preventing RAG from bypassing evidence logging
- Add source-tier policies by audience and report type
- Add editor-fixable vs analyst-blocking audit classifications

## Long-Term

- Add opt-in internal message ingestion with allowlists, denylists, and redaction gates
- Add database and semantic-layer adapters for structured metrics
- Add multi-model routing for scout, analyst, audit, and edit steps
- Add enterprise deployment patterns with strict credential handling
- Add evaluation suites for overclaiming, stale evidence, and unsupported recommendations

## Safety Principle

Every roadmap item should ship with public or synthetic examples, tests, documentation, and no credentials or sensitive workflow artifacts.
