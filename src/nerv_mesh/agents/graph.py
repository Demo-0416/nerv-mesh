"""Agent graph construction — the core of nerv-mesh."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent

from nerv_mesh.config.models import AppConfig
from nerv_mesh.llm import resolve_model
from nerv_mesh.memory import MemoryStore
from nerv_mesh.sandbox import LocalSandbox
from nerv_mesh.skills import SkillLoader
from nerv_mesh.tools import aggregate_tools

_SYSTEM_PROMPT_TEMPLATE = """\
You are nerv-mesh, a general-purpose AI agent.

## Capabilities
- Read, write, and edit files
- Execute shell commands
- Search files and code with grep/glob
- Search the web and fetch URL content
- Manage your own skills and MCP extensions
- Analyze, summarize, translate, explain, and research

## Guidelines
- Explain your reasoning before taking actions
- Use the right tool for the job
- Verify results after making changes
- Ask for clarification when the task is ambiguous

{memory_context}"""


def build_agent(
    config: AppConfig,
    sandbox: LocalSandbox,
    memory: MemoryStore,
    skills: SkillLoader | None = None,
) -> CompiledStateGraph:
    """Assemble the lead agent: model + tools + prompt + checkpointer."""
    model = resolve_model(config.models["default"])
    tools = aggregate_tools(config, sandbox, skills)
    prompt = _build_system_prompt(memory, skills)

    return create_react_agent(
        model,
        tools,
        prompt=prompt,
        checkpointer=MemorySaver(),
    )


def _build_system_prompt(
    memory: MemoryStore, skills: SkillLoader | None = None
) -> str:
    parts = [memory.get_context()]
    if skills:
        fragment = skills.prompt_fragment()
        if fragment:
            parts.append(fragment)
    return _SYSTEM_PROMPT_TEMPLATE.format(memory_context="\n\n".join(filter(None, parts)))
