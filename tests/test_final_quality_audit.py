from multi_agent_brief.audit.final_quality import FinalQualityAuditAgent, FinalQualityConfig
from multi_agent_brief.core.claim_ledger import ClaimLedger
from multi_agent_brief.core.schemas import PipelineContext


def test_final_quality_blocks_thin_normal_report():
    report = FinalQualityAuditAgent(FinalQualityConfig(min_markdown_chars=100)).run_audit(
        "# Brief\n\nToo short.",
        ClaimLedger(),
    )

    assert report.audit_status == "fail"
    assert any(f.finding_type == "final_report_too_thin" for f in report.findings)
    assert report.metadata["harness_protocol"] == "BRIEF_HARNESS_V2"


def test_final_quality_allows_quiet_week_depth_exception():
    report = FinalQualityAuditAgent(FinalQualityConfig(min_markdown_chars=100, quiet_week=True)).run_audit(
        "# Brief\n\nToo short.",
        ClaimLedger(),
    )

    assert not any(f.finding_type == "final_report_too_thin" for f in report.findings)


def test_final_quality_checks_summary_bullet_count():
    markdown = """# Brief

## Executive Summary

▸ One
▸ Two
"""

    report = FinalQualityAuditAgent(
        FinalQualityConfig(min_markdown_chars=0, expected_summary_bullets=5, required_metadata_labels=[])
    ).run_audit(markdown, ClaimLedger())

    assert any(f.finding_type == "summary_bullet_count_mismatch" for f in report.findings)


def test_final_quality_blocks_wide_markdown_tables():
    markdown = """# Brief

## Executive Summary

| A | B | C | D | E |
| - | - | - | - | - |
"""

    report = FinalQualityAuditAgent(
        FinalQualityConfig(min_markdown_chars=0, expected_summary_bullets=None, required_metadata_labels=[])
    ).run_audit(markdown, ClaimLedger())

    assert any(f.finding_type == "wide_markdown_table" for f in report.findings)


def test_final_quality_flags_stale_date_framed_as_current():
    context = PipelineContext(
        project_name="Demo",
        input_dir="input",
        output_dir="output",
        report_date="2026-06-02",
        max_source_age_days=14,
    )
    markdown = "This week, the 2026-04-01 policy update remains the latest development."

    report = FinalQualityAuditAgent(
        FinalQualityConfig(min_markdown_chars=0, expected_summary_bullets=None, required_metadata_labels=[])
    ).run_audit(markdown, ClaimLedger(), context)

    assert any(f.finding_type == "stale_date_framed_as_current" for f in report.findings)


def test_final_quality_requires_docx_when_configured(tmp_path):
    missing_docx = tmp_path / "missing.docx"

    report = FinalQualityAuditAgent(
        FinalQualityConfig(
            min_markdown_chars=0,
            expected_summary_bullets=None,
            required_metadata_labels=[],
            rendered_docx_path=str(missing_docx),
        )
    ).run_audit("# Brief", ClaimLedger())

    assert any(f.finding_type == "missing_rendered_docx" for f in report.findings)
