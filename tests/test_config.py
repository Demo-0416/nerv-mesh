"""Tests for the multi-file config layer."""

import json

import pytest
import yaml

from nerv_mesh.config import AppConfig, load_config
from nerv_mesh.config.loader import _resolve_env_vars


@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    """Create a temporary ~/.nerv-mesh/ with valid config."""
    monkeypatch.setenv("NERV_MESH_HOME", str(tmp_path))
    (tmp_path / "config.yaml").write_text(yaml.dump({"sandbox": {"mode": "local"}}))
    (tmp_path / "models.yaml").write_text(yaml.dump({
        "default": {
            "provider": "langchain_openai:ChatOpenAI",
            "base_url": "https://coding.dashscope.aliyuncs.com/v1",
            "api_key": "test-key",
            "model": "MiniMax-M2.5",
        }
    }))
    (tmp_path / "mcp.json").write_text('{"mcpServers": {}}')
    (tmp_path / "settings.json").write_text(json.dumps({
        "default_model": "default",
        "memory": {"enabled": True},
    }))
    (tmp_path / "skills" / "custom").mkdir(parents=True)
    return tmp_path


def test_load_config_from_home(fake_home):
    config = load_config()
    assert isinstance(config, AppConfig)
    assert "default" in config.models
    assert config.sandbox.mode == "local"


def test_model_config_fields(fake_home):
    config = load_config()
    default = config.models["default"]
    assert default.model == "MiniMax-M2.5"
    assert "coding.dashscope" in (default.base_url or "")


def test_settings_loaded(fake_home):
    config = load_config()
    assert config.memory.enabled is True
    assert config.settings.default_model == "default"


def test_mcp_loaded(fake_home):
    config = load_config()
    assert config.mcp.mcpServers == {}


def test_property_shortcuts(fake_home):
    config = load_config()
    assert config.feishu == config.settings.feishu
    assert config.memory == config.settings.memory
    assert config.skills_config == config.settings.skills


def test_auto_create_defaults(tmp_path, monkeypatch):
    """First-run should copy default configs from package."""
    monkeypatch.setenv("NERV_MESH_HOME", str(tmp_path))
    load_config()
    assert (tmp_path / "config.yaml").exists()
    assert (tmp_path / "models.yaml").exists()


def test_resolve_env_vars_simple(monkeypatch):
    monkeypatch.setenv("TEST_KEY", "secret123")
    assert _resolve_env_vars("$TEST_KEY") == "secret123"


def test_resolve_env_vars_missing():
    assert _resolve_env_vars("$DEFINITELY_NOT_SET_XYZ") == ""


def test_resolve_env_vars_nested(monkeypatch):
    monkeypatch.setenv("K", "v")
    result = _resolve_env_vars({"a": "$K", "b": ["$K", "literal"]})
    assert result == {"a": "v", "b": ["v", "literal"]}


def test_resolve_env_vars_passthrough():
    assert _resolve_env_vars(42) == 42
    assert _resolve_env_vars("no-dollar") == "no-dollar"
