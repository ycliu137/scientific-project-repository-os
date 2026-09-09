"""Pipeline smoke: OS tools import. Source package tests live in the source sibling."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_constitution_exists():
    assert (ROOT / "SKILL.md").is_file()
    assert (ROOT / "os.yaml").is_file()


def test_bridge_importable():
    import sys

    sys.path.insert(0, str(ROOT / "tools"))
    import os_config  # noqa: F401


def test_env_layout():
    assert (ROOT / "env" / "README.md").is_file()
    assert (ROOT / "env" / "catalog.yaml").is_file()
    template = ROOT / "env" / "_TEMPLATE.sh"
    assert template.is_file()
    text = template.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env bash")
    assert "micromamba" in text
    readme = (ROOT / "env" / "README.md").read_text(encoding="utf-8")
    assert "create_<name>.sh" in readme


def test_smoke_lives_under_tests():
    assert (ROOT / "tests" / "smoke" / "README.md").is_file()
    assert not (ROOT / "smoke").exists()


def test_map_is_contract_table():
    text = (ROOT / "MAP.md").read_text(encoding="utf-8")
    assert "index/domain_inventory.generated.yaml" in text
    assert "Contract" in text or "contract" in text
    assert "| scaffold |" not in text.lower()
    assert not (ROOT / "workspace" / "scratch").exists()


def test_language_skill_and_h18():
    assert (ROOT / "skills" / "language.md").is_file()
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "Project language is English" in skill
    lang = (ROOT / "skills" / "language.md").read_text(encoding="utf-8")
    assert "tex_docs/" in lang
    assert "meeting_record/" in lang


def test_notation_skill_and_h21():
    assert (ROOT / "skills" / "notation.md").is_file()
    assert (ROOT / "docs" / "NOTATION.md").is_file()
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "Unified notation" in skill
    notation = (ROOT / "skills" / "notation.md").read_text(encoding="utf-8")
    assert "docs/NOTATION.md" in notation
    registry = (ROOT / "docs" / "NOTATION.md").read_text(encoding="utf-8")
    assert "Math" in registry
    assert "Code" in registry


def test_module_template_path_contract_when_present():
    """pipelines/ is instance-grown; only assert if the template folder exists."""
    path = ROOT / "pipelines" / "_TEMPLATE" / "README.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    for heading in ("Purpose", "Inputs", "Outputs", "Relations", "How to run", "Path contract"):
        assert f"## {heading}" in text
