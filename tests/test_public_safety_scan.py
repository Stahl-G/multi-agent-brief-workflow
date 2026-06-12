from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_public_safety.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_public_safety_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_public_safety_scan_uses_env_banned_terms_without_repo_denylist(tmp_path):
    module = _load_module()
    sample = tmp_path / "sample.md"
    sample.write_text("Private release candidate mentions ACME_PRIVATE.\n", encoding="utf-8")

    findings = module.scan([sample], banned_terms=["ACME_PRIVATE"])

    assert len(findings) == 1
    assert findings[0].kind == "banned_term"
    assert findings[0].path == sample


def test_public_safety_scan_allows_fake_test_tokens(tmp_path):
    module = _load_module()
    module.ROOT = tmp_path
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    fake_path = test_dir / "fake_safety_fixture_for_unit_test.md"
    fake_path.write_text(
        "Example recipient oc_secret_chat and file:///Users/example/source.md\n",
        encoding="utf-8",
    )

    findings = module.scan([fake_path], banned_terms=[])

    assert findings == []


def test_public_safety_scan_catches_lark_recipient_and_file_token_prefixes(tmp_path):
    module = _load_module()
    sample = tmp_path / "candidate_pack.md"
    sample.write_text(
        "\n".join(
            [
                "folder fld1234567890abcdef",
                "open message on1234567890abcdef",
                "cli token cli1234567890abcdef",
                "file token f1234567890abcdef",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    findings = module.scan([sample], banned_terms=[])

    assert [finding.kind for finding in findings] == [
        "lark_token",
        "lark_token",
        "lark_token",
        "lark_token",
    ]


def test_public_safety_scan_does_not_flag_common_words_starting_with_token_prefixes(tmp_path):
    module = _load_module()
    sample = tmp_path / "public_docs.md"
    sample.write_text(
        "finalize formatter freshness file_path client onboarding folder\n",
        encoding="utf-8",
    )

    findings = module.scan([sample], banned_terms=[])

    assert findings == []
