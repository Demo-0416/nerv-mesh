"""Tests for meta-tools (self-evolution capabilities)."""

import json

from nerv_mesh.config import AppConfig
from nerv_mesh.skills import SkillLoader
from nerv_mesh.tools.meta import make_meta_tools


def test_introspect(tmp_path, monkeypatch):
    monkeypatch.setenv("NERV_MESH_HOME", str(tmp_path))
    (tmp_path / "skills" / "custom").mkdir(parents=True)
    config = _minimal_config()
    skills = SkillLoader()
    tools = make_meta_tools(config, skills)
    introspect = next(t for t in tools if t.name == "introspect")
    result = introspect.invoke({})
    assert "test-model" in result
    assert "skill-creator" in result


def test_skill_create(tmp_path, monkeypatch):
    monkeypatch.setenv("NERV_MESH_HOME", str(tmp_path))
    (tmp_path / "skills" / "custom").mkdir(parents=True)

    config = _minimal_config()
    skills = SkillLoader()
    tools = make_meta_tools(config, skills)
    create = next(t for t in tools if t.name == "skill_create")

    result = create.invoke({
        "name": "test-skill",
        "description": "A test skill",
        "instructions": "Do the thing.",
    })
    assert "created" in result.lower()
    assert (tmp_path / "skills/custom/test-skill/SKILL.md").exists()


def test_mcp_install_and_remove(tmp_path, monkeypatch):
    monkeypatch.setenv("NERV_MESH_HOME", str(tmp_path))
    (tmp_path / "mcp.json").write_text('{"mcpServers": {}}')

    config = _minimal_config()
    skills = SkillLoader()
    tools = make_meta_tools(config, skills)
    install = next(t for t in tools if t.name == "mcp_install")
    remove = next(t for t in tools if t.name == "mcp_remove")

    result = install.invoke({
        "name": "test-server",
        "command": "npx",
        "cmd_args": "-y @test/server",
    })
    assert "installed" in result.lower()

    data = json.loads((tmp_path / "mcp.json").read_text())
    assert "test-server" in data["mcpServers"]

    result = remove.invoke({"name": "test-server"})
    assert "removed" in result.lower()

    data = json.loads((tmp_path / "mcp.json").read_text())
    assert "test-server" not in data["mcpServers"]


def _minimal_config() -> AppConfig:
    return AppConfig(models={"default": {"model": "test-model"}})
