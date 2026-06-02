from multi_agent_brief.core.config import build_run_settings, load_config


def test_old_project_language_still_loads(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
project:
  name: "Legacy Brief"
  language: "en-US"
  audience: "management"
input:
  path: "input"
output:
  path: "output"
""",
        encoding="utf-8",
    )

    config = load_config(config_path)
    settings = build_run_settings(
        config=config,
        input_dir=None,
        output_dir=None,
        name=None,
        language=None,
        audience=None,
    )

    assert config["language"]["interface"] == "en-US"
    assert config["language"]["output"] == "en-US"
    assert config["language"]["source_handling"] == "preserve_original"
    assert settings["language"] == "en-US"


def test_missing_language_defaults_to_chinese(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
project:
  name: "Default Brief"
input:
  path: "input"
output:
  path: "output"
""",
        encoding="utf-8",
    )

    config = load_config(config_path)
    settings = build_run_settings(
        config=config,
        input_dir=None,
        output_dir=None,
        name=None,
        language=None,
        audience=None,
    )

    assert config["language"]["interface"] == "zh-CN"
    assert config["language"]["output"] == "zh-CN"
    assert settings["language"] == "zh-CN"
