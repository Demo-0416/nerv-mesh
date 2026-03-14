"""Dynamic LLM model resolution from config."""

import importlib

from langchain_core.language_models import BaseChatModel

from nerv_mesh.config.models import ModelConfig


def resolve_model(config: ModelConfig) -> BaseChatModel:
    """Instantiate a chat model from a provider string like 'langchain_openai:ChatOpenAI'."""
    model_cls = _import_class(config.provider)
    kwargs = _build_kwargs(config)
    return model_cls(**kwargs)


def _import_class(provider: str) -> type:
    """Dynamically import 'module.path:ClassName'."""
    module_path, class_name = provider.rsplit(":", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name, None)
    if cls is None:
        raise ImportError(f"Class '{class_name}' not found in '{module_path}'")
    return cls


def _build_kwargs(config: ModelConfig) -> dict:
    """Build constructor kwargs, omitting None values."""
    kwargs: dict = {"model": config.model, "temperature": config.temperature}
    if config.base_url:
        kwargs["base_url"] = config.base_url
    if config.api_key:
        kwargs["api_key"] = config.api_key
    if config.max_tokens:
        kwargs["max_tokens"] = config.max_tokens
    return kwargs
