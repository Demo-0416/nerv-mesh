"""Tool aggregation — assembles tools from builtins + meta + config."""

import importlib

from langchain_core.tools import BaseTool

from nerv_mesh.config.models import AppConfig, ToolRef
from nerv_mesh.sandbox.local import LocalSandbox
from nerv_mesh.skills import SkillLoader

from .builtin import make_builtin_tools
from .meta import make_meta_tools


def aggregate_tools(
    config: AppConfig,
    sandbox: LocalSandbox,
    skills: SkillLoader | None = None,
) -> list[BaseTool]:
    """Collect all available tools: builtins + meta + config-defined."""
    tools: list[BaseTool] = []
    tools.extend(make_builtin_tools(sandbox))
    if skills:
        tools.extend(make_meta_tools(config, skills))
    tools.extend(_load_config_tools(config.tools))
    return tools


def _load_config_tools(refs: list[ToolRef]) -> list[BaseTool]:
    """Dynamically import tools declared in config.yaml."""
    tools: list[BaseTool] = []
    for ref in refs:
        if not ref.enabled:
            continue
        tools.append(_import_tool(ref))
    return tools


def _import_tool(ref: ToolRef) -> BaseTool:
    """Import a single tool from 'module.path:name' string."""
    module_path, attr_name = ref.use.rsplit(":", 1)
    module = importlib.import_module(module_path)
    tool_obj = getattr(module, attr_name, None)
    if tool_obj is None:
        raise ImportError(f"Tool '{attr_name}' not found in '{module_path}'")
    return tool_obj
