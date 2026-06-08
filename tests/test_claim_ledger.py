import json

from multi_agent_brief.core.claim_ledger import ClaimLedger
from multi_agent_brief.core.schemas import Claim


def test_claim_ledger_add_get_and_validate():
    ledger = ClaimLedger()
    claim = Claim(
        claim_id="TEST_123456",
        statement="Revenue increased 10%.",
        source_id="SOURCE_A",
        evidence_text="Revenue increased 10% in the synthetic source.",
    )

    ledger.add_claim(claim)

    assert ledger.get_claim("TEST_123456") == claim
    assert ledger.validate_claims() == []


def test_claim_ledger_detects_missing_sources():
    ledger = ClaimLedger(
        [
            Claim(
                claim_id="TEST_123456",
                statement="Revenue increased 10%.",
                source_id="",
                evidence_text="",
            )
        ]
    )

    assert len(ledger.detect_missing_sources()) == 1
    assert ledger.validate_claims()


def test_claim_ledger_import_accepts_manifest_wrapper(tmp_path):
    path = tmp_path / "claim_ledger.json"
    path.write_text(
        json.dumps(
            {
                "metadata": {"generated_by": "synthetic fixture"},
                "claims": [
                    {
                        "claim_id": "CLM-001",
                        "statement": "Revenue increased 10%.",
                        "source_id": "SOURCE_A",
                        "evidence_text": "Revenue increased 10% in the synthetic source.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    ledger = ClaimLedger.import_json(path)

    assert len(ledger) == 1
    assert ledger.get_claim("CLM-001") is not None
