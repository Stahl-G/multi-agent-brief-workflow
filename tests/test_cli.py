from pathlib import Path

from multi_agent_brief.cli.main import main


def test_cli_init_and_run(tmp_path):
    workspace = tmp_path / "ws"

    assert main(["init", str(workspace), "--language", "zh-CN", "--industry", "finance"]) == 0
    assert (workspace / "config.yaml").exists()
    assert (workspace / "sources.yaml").exists()

    # Add a source file
    (workspace / "input").mkdir(exist_ok=True)
    (workspace / "input" / "news.md").write_text("- Test signal for weekly brief.\n", encoding="utf-8")

    assert main(["run", "--config", str(workspace / "config.yaml")]) == 0
    assert (workspace / "output" / "brief.md").exists()
    assert (workspace / "output" / "claim_ledger.json").exists()


def test_cli_run_with_industry(tmp_path):
    workspace = tmp_path / "ws"
    main(["init", str(workspace), "--language", "zh-CN", "--industry", "finance"])

    (workspace / "input").mkdir(exist_ok=True)
    (workspace / "input" / "data.md").write_text("- Financial earnings report shows growth.\n", encoding="utf-8")

    assert main(["run", "--config", str(workspace / "config.yaml"), "--industry", "finance"]) == 0
    assert (workspace / "output" / "brief.md").exists()


def test_cli_audit_existing_brief(tmp_path):
    workspace = tmp_path / "ws"
    main(["init", str(workspace), "--language", "zh-CN"])
    (workspace / "input").mkdir(exist_ok=True)
    (workspace / "input" / "news.md").write_text("- Test signal for audit.\n", encoding="utf-8")
    main(["run", "--config", str(workspace / "config.yaml")])

    audit_output = tmp_path / "audit.json"
    exit_code = main(
        [
            "audit",
            str(workspace / "output" / "brief.md"),
            "--ledger",
            str(workspace / "output" / "claim_ledger.json"),
            "--output",
            str(audit_output),
            "--report-date",
            "2026-06-02",
            "--max-source-age-days",
            "14",
            "--fail-on-stale-source",
        ]
    )

    assert exit_code == 0
    assert '"audit_status": "pass"' in audit_output.read_text(encoding="utf-8")


def test_cli_version(capsys):
    assert main(["version"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip()
