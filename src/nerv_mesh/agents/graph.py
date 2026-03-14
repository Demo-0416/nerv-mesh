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
You are nerv-mesh, an AI coding assistant.

## Capabilities
- Read and write files in the project
- Execute shell commands (build, test, git, etc.)
- Analyze code and suggest improvements
- Help with debugging, refactoring, and implementation

## Guidelines
- Explain your reasoning before taking actions
- Prefer small, focused changes over large rewrites
- Verify your changes by reading the result or running tests
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
