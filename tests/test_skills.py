"""Tests for the skills system."""

from nerv_mesh.skills import SkillLoader


def test_discover_builtin_skills(tmp_path, monkeypatch):
    monkeypatch.setenv("NERV_MESH_HOME", str(tmp_path))
    (tmp_path / "skills" / "custom").mkdir(parents=True)
    loader = SkillLoader()
    skills = loader.list_skills()
    names = {s["name"] for s in skills}
    assert "skill-creator" in names
    assert "code-review" in names


def test_get_skill_by_name(tmp_path, monkeypatch):
    monkeypatch.setenv("NERV_MESH_HOME", str(tmp_path))
    (tmp_path / "skills" / "custom").mkdir(parents=True)
    loader = SkillLoader()
    skill = loader.get("skill-creator")
    assert skill is not None
    assert skill.name == "skill-creator"
    assert skill.description != ""


def test_load_instructions(tmp_path, monkeypatch):
    monkeypatch.setenv("NERV_MESH_HOME", str(tmp_path))
    (tmp_path / "skills" / "custom").mkdir(parents=True)
    loader = SkillLoader()
    instructions = loader.load_instructions("skill-creator")
    assert instructions is not None
    assert "skill" in instructions.lower()


def test_prompt_fragment(tmp_path, monkeypatch):
    monkeypatch.setenv("NERV_MESH_HOME", str(tmp_path))
    (tmp_path / "skills" / "custom").mkdir(parents=True)
    loader = SkillLoader()
    fragment = loader.prompt_fragment()
    assert "skill-creator" in fragment
    assert "code-review" in fragment


def test_get_missing_skill(tmp_path, monkeypatch):
    monkeypatch.setenv("NERV_MESH_HOME", str(tmp_path))
    (tmp_path / "skills" / "custom").mkdir(parents=True)
    loader = SkillLoader()
    assert loader.get("nonexistent") is None
    assert loader.load_instructions("nonexistent") is None


def test_custom_skill(tmp_path, monkeypatch):
    monkeypatch.setenv("NERV_MESH_HOME", str(tmp_path))
    custom_dir = tmp_path / "skills" / "custom" / "my-tool"
    custom_dir.mkdir(parents=True)
    (custom_dir / "SKILL.md").write_text(
        "---\nname: my-tool\ndescription: test skill\n---\n\nDo the thing."
    )
    loader = SkillLoader()
    skill = loader.get("my-tool")
    assert skill is not None
    assert skill.instructions == "Do the thing."
