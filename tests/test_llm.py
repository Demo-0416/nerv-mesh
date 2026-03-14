"""Tests for the LLM resolver."""

import pytest

from nerv_mesh.config.models import ModelConfig
from nerv_mesh.llm.resolver import _build_kwargs, _import_class


def test_import_class_valid():
    cls = _import_class("langchain_openai:ChatOpenAI")
    assert cls.__name__ == "ChatOpenAI"


def test_import_class_invalid_module():
    with pytest.raises(ModuleNotFoundError):
        _import_class("nonexistent_module:SomeClass")


def test_import_class_invalid_attr():
    with pytest.raises(ImportError, match="not found"):
        _import_class("langchain_openai:NonexistentClass")


def test_build_kwargs_minimal():
    config = ModelConfig(model="gpt-4", temperature=0.5)
    kwargs = _build_kwargs(config)
    assert kwargs == {"model": "gpt-4", "temperature": 0.5}


def test_build_kwargs_with_optional_fields():
    config = ModelConfig(
        model="qwen3.5-plus",
        temperature=0.7,
        base_url="https://example.com/v1",
        api_key="sk-test",
        max_tokens=4096,
    )
    kwargs = _build_kwargs(config)
    assert kwargs["base_url"] == "https://example.com/v1"
    assert kwargs["api_key"] == "sk-test"
    assert kwargs["max_tokens"] == 4096
