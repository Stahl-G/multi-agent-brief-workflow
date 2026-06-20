from __future__ import annotations

from multi_agent_brief.orchestrator.runtime_state.claim_support_matrix import (
    CLAIM_SUPPORT_MATRIX_POLICY_PROJECTION_SCHEMA_VERSION,
    project_claim_support_matrix_policy,
    project_claim_support_policy,
)


def _row(
    row_id: str,
    *,
    atom_id: str = "AC-0001-01",
    claim_id: str = "CL-0001",
    evidence_span_id: str | None = "ESP-001-01",
    support_label: str = "direct_support",
    support_strength: str = "high",
    required_action: str = "none",
    repair_owner: str = "none",
    decision_source: str = "human",
) -> dict:
    return {
        "row_id": row_id,
        "claim_id": claim_id,
        "atom_id": atom_id,
        "evidence_span_id": evidence_span_id,
        "support_label": support_label,
        "support_strength": support_strength,
        "support_reason": "Recorded support relation for deterministic policy projection.",
        "required_action": required_action,
        "repair_owner": repair_owner,
        "decision_source": decision_source,
    }


def test_claim_support_policy_empty_rows_is_not_available():
    projection = project_claim_support_policy(rows=[], atom_materiality={})

    assert projection["schema_version"] == CLAIM_SUPPORT_MATRIX_POLICY_PROJECTION_SCHEMA_VERSION
    assert projection["status"] == "not_available"
    assert projection["row_count"] == 0
    assert projection["atom_count"] == 0
    assert projection["summary_counts"]["blocking_atom_count"] == 0


def test_high_materiality_unsupported_row_projects_blocking_atom():
    projection = project_claim_support_policy(
        rows=[
            _row(
                "CSM-0001",
                evidence_span_id=None,
                support_label="unsupported",
                support_strength="none",
                required_action="add_evidence_span",
                repair_owner="analyst",
            )
        ],
        atom_materiality={"AC-0001-01": "high"},
    )

    atom = projection["atoms"][0]
    assert projection["status"] == "projected"
    assert atom["blocking"] is True
    assert atom["verdict"] == "blocking"
    assert atom["blocking_rows"][0]["row_id"] == "CSM-0001"
    assert projection["summary_counts"]["blocking_row_count"] == 1


def test_low_materiality_unsupported_row_does_not_block_without_policy_action():
    projection = project_claim_support_policy(
        rows=[
            _row(
                "CSM-0001",
                evidence_span_id=None,
                support_label="unsupported",
                support_strength="none",
                required_action="none",
            )
        ],
        atom_materiality={"AC-0001-01": "low"},
    )

    atom = projection["atoms"][0]
    assert atom["blocking"] is False
    assert atom["verdict"] == "recorded"
    assert projection["summary_counts"]["blocking_atom_count"] == 0


def test_block_release_action_projects_blocking_regardless_of_materiality():
    projection = project_claim_support_policy(
        rows=[
            _row(
                "CSM-0001",
                support_label="partial_support",
                support_strength="medium",
                required_action="block_release",
                repair_owner="human_review",
            )
        ],
        atom_materiality={"AC-0001-01": "low"},
    )

    atom = projection["atoms"][0]
    assert atom["blocking"] is True
    assert atom["verdict"] == "blocking"
    assert atom["blocking_rows"][0]["required_action"] == "block_release"


def test_weak_support_projects_weak_and_downgrade_signals():
    projection = project_claim_support_policy(
        rows=[
            _row(
                "CSM-0001",
                support_label="weak_support",
                support_strength="low",
                required_action="downgrade_wording",
                repair_owner="editor",
            )
        ],
        atom_materiality={"AC-0001-01": "medium"},
    )

    atom = projection["atoms"][0]
    assert atom["weak_support"] is True
    assert atom["downgrade_required"] is True
    assert atom["verdict"] == "downgrade_required"
    assert atom["weak_rows"][0]["row_id"] == "CSM-0001"
    assert atom["downgrade_required_rows"][0]["repair_owner"] == "editor"


def test_human_adjudication_action_projects_adjudication_signal():
    projection = project_claim_support_policy(
        rows=[
            _row(
                "CSM-0001",
                support_label="partial_support",
                support_strength="medium",
                required_action="human_adjudication",
                repair_owner="human_review",
            )
        ],
        atom_materiality={"AC-0001-01": "medium"},
    )

    atom = projection["atoms"][0]
    assert atom["adjudication_required"] is True
    assert atom["verdict"] == "adjudication_required"
    assert atom["adjudication_required_rows"][0]["decision_source"] == "human"


def test_inferential_support_projects_framing_signal():
    projection = project_claim_support_policy(
        rows=[
            _row(
                "CSM-0001",
                support_label="inferential_support",
                support_strength="medium",
                required_action="mark_as_inference",
                repair_owner="analyst",
            )
        ],
        atom_materiality={"AC-0001-01": "high"},
    )

    atom = projection["atoms"][0]
    assert atom["inference_framing_required"] is True
    assert atom["verdict"] == "inference_framing_required"
    assert atom["inference_framing_required_rows"][0]["required_action"] == "mark_as_inference"


def test_multiple_rows_for_same_atom_aggregate_stably():
    projection = project_claim_support_policy(
        rows=[
            _row(
                "CSM-0002",
                support_label="weak_support",
                support_strength="low",
                required_action="downgrade_wording",
                repair_owner="editor",
                decision_source="llm_assisted_human",
            ),
            _row(
                "CSM-0001",
                support_label="direct_support",
                support_strength="high",
                required_action="none",
                repair_owner="none",
                decision_source="human",
            ),
        ],
        atom_materiality={"AC-0001-01": "medium"},
    )

    atom = projection["atoms"][0]
    assert atom["row_ids"] == ["CSM-0001", "CSM-0002"]
    assert atom["support_labels"] == ["direct_support", "weak_support"]
    assert atom["support_strengths"] == ["high", "low"]
    assert atom["required_actions"] == ["downgrade_wording", "none"]
    assert atom["repair_owners"] == ["editor", "none"]
    assert atom["decision_sources"] == ["human", "llm_assisted_human"]
    assert atom["downgrade_required_rows"][0]["row_id"] == "CSM-0002"


def test_project_claim_support_matrix_policy_uses_payload_rows_and_materiality():
    projection = project_claim_support_matrix_policy(
        {
            "schema_version": "mabw.claim_support_matrix.v1",
            "rows": [
                _row(
                    "CSM-0001",
                    atom_id="AC-0002-01",
                    claim_id="CL-0002",
                    evidence_span_id=None,
                    support_label="insufficient_evidence",
                    support_strength="none",
                    required_action="add_evidence_span",
                )
            ],
        },
        atom_materiality={"AC-0002-01": "high"},
    )

    atom = projection["atoms"][0]
    assert atom["atom_id"] == "AC-0002-01"
    assert atom["claim_id"] == "CL-0002"
    assert atom["materiality"] == "high"
    assert atom["blocking"] is True
