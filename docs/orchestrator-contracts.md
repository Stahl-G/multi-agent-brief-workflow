# Orchestrator Contract Model

v0.6 is organized around four public contract categories. This page defines them at an abstract level only. Detailed schema drafts, private prompt notes, evaluation cases, and commercial policy rules are kept out of the public repository until they are stable.

## Behavior Contract

Defines role boundaries: what the main Orchestrator may coordinate, what specialist subagents are responsible for, and which actions should be blocked or escalated.

## Process / Artifact Contract

Defines whether the workflow has progressed through required stages and whether expected artifacts exist before downstream work proceeds.

## Fact-Grounding / Evidence Contract

Defines the expectation that important statements remain traceable to source-grounded evidence, and that unsupported or uncertain claims are not overstated.

v0.6.5 provenance projection can expose citation and control relationships for audit/debug review, but it does not assert semantic truth or replace human evidence review.

`provenance_graph.json` is produced by a Python control tool, not by a formal workflow stage. Artifact contracts mark this with `producer_kind: control_tool`; `producer_stage: provenance` is a control-tool pseudo-producer label, not a `stage_specs.yaml` stage.

For provenance graph edges, `artifact_derived_from` is directional: `from` is the derived/output artifact and `to` is the source/input artifact.

## Quality / Audience Contract

Defines whether the delivered brief is useful for the intended reader, matches the task context, and meets delivery-readiness expectations.

## Public Boundary

This public model intentionally does not publish full schema drafts, exact validation rules, private golden cases, industry-specific policy packs, or agent prompt details.
