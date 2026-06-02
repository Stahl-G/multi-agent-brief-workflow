from argparse import Namespace

from multi_agent_brief.cli.init_wizard import build_profile_from_args, prompt_for_profile
from multi_agent_brief.cli.main import main


def test_init_demo_preserves_existing_demo_behavior(tmp_path):
    demo_dir = tmp_path / "demo"

    assert main(["init", str(demo_dir), "--demo"]) == 0

    assert (demo_dir / "config.yaml").exists()
    assert (demo_dir / "input" / "news.json").exists()
    assert (demo_dir / "input" / "market_data.json").exists()


def test_init_workspace_creates_expected_files(tmp_path):
    workspace = tmp_path / "workspace"

    assert main(["init", str(workspace), "--language", "zh-CN"]) == 0

    assert (workspace / "config.yaml").exists()
    assert (workspace / "profile.yaml").exists()
    assert (workspace / "sources.yaml").exists()
    assert (workspace / "input" / "README.md").exists()
    assert (workspace / "output").is_dir()
    assert (workspace / ".gitignore").exists()


def test_language_prompt_is_first_and_defaults_to_chinese():
    prompts = []

    def fake_input(prompt):
        prompts.append(prompt)
        return ""

    profile = prompt_for_profile(input_func=fake_input)

    assert prompts[0].startswith("Select language / 选择语言")
    assert "请输入公司名称" in prompts[1]
    assert profile.interface_language == "zh-CN"
    assert profile.output_language == "zh-CN"


def test_english_mode_generates_english_config_values(tmp_path):
    workspace = tmp_path / "english"

    assert (
        main(
            [
                "init",
                str(workspace),
                "--language",
                "en-US",
                "--company",
                "Sample Solar Manufacturer",
                "--role",
                "strategy_office",
                "--industry",
                "solar",
                "--title",
                "Weekly Solar Industry Brief",
                "--audience",
                "management",
                "--cadence",
                "weekly",
                "--rag",
                "off",
            ]
        )
        == 0
    )

    config_text = (workspace / "config.yaml").read_text(encoding="utf-8")
    assert 'interface: "en-US"' in config_text
    assert 'output: "en-US"' in config_text
    assert 'company: "Sample Solar Manufacturer"' in config_text
    assert 'enabled: false' in config_text


def test_bilingual_mode_sets_interface_and_output():
    args = Namespace(
        language="bilingual",
        output_language=None,
        company=None,
        role=None,
        industry=None,
        title=None,
        audience=None,
        focus_areas=None,
        cadence=None,
        rag="off",
        retrieval_provider=None,
        selector_max_items=None,
        output_formats=None,
    )

    profile = build_profile_from_args(args)

    assert profile.interface_language == "bilingual"
    assert profile.output_language == "bilingual"


def test_rag_provider_can_be_set_to_ollama_or_gemini():
    base = dict(
        language="zh-CN",
        output_language=None,
        company=None,
        role=None,
        industry=None,
        title=None,
        audience=None,
        focus_areas=None,
        cadence=None,
        selector_max_items=None,
        output_formats=None,
    )
    ollama = build_profile_from_args(Namespace(**base, rag="on", retrieval_provider="ollama"))
    gemini = build_profile_from_args(Namespace(**base, rag="on", retrieval_provider="gemini"))

    assert ollama.retrieval_enabled is True
    assert ollama.retrieval_provider == "ollama"
    assert ollama.retrieval_model == "nomic-embed-text"
    assert gemini.retrieval_enabled is True
    assert gemini.retrieval_provider == "gemini"
    assert gemini.retrieval_model == "gemini-embedding-001"


def test_workspace_gitignore_excludes_private_and_generated_paths(tmp_path):
    workspace = tmp_path / "workspace"

    main(["init", str(workspace), "--language", "zh-CN"])

    gitignore = (workspace / ".gitignore").read_text(encoding="utf-8")
    for expected in [".env", "output/", ".rag/", "private_inputs/", "private_outputs/"]:
        assert expected in gitignore


def test_generated_input_readme_is_not_treated_as_source(tmp_path):
    workspace = tmp_path / "workspace"

    main(["init", str(workspace), "--language", "zh-CN"])
    assert main(["run", "--config", str(workspace / "config.yaml")]) == 0

    ledger = (workspace / "output" / "claim_ledger.json").read_text(encoding="utf-8")
    assert ledger.strip() == "[]"
