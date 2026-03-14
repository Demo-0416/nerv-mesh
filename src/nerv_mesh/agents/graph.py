"""Agent graph construction — the core of nerv-mesh."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent

from nerv_mesh.config.models import AppConfig
from nerv_mesh.llm import resolve_model
from nerv_mesh.memory import MemoryStore
from nerv_mesh.memory.profile import load_profile
from nerv_mesh.sandbox import LocalSandbox
from nerv_mesh.skills import SkillLoader
from nerv_mesh.tools import aggregate_tools

_BASE_PROMPT = """\
You are nerv-mesh, a general-purpose AI agent.

## Capabilities
- Read, write, and edit files
- Execute shell commands
- Search files and code with grep/glob
- Search the web and fetch URL content
- Manage your own skills and MCP extensions
- Read and update persistent memory (SOUL.md, USER.md, NERV.md)
- Analyze, summarize, translate, explain, and research

## Guidelines
- Use the right tool for the job
- Verify results after making changes
- Ask for clarification when the task is ambiguous
- Update USER.md when you learn important facts about the user
- Update SOUL.md when you learn lessons about how to be more helpful"""


def build_agent(
    config: AppConfig,
    sandbox: LocalSandbox,
    memory: MemoryStore,
    skills: SkillLoader | None = None,
) -> CompiledStateGraph:
    """Assemble the lead agent: model + tools + prompt + checkpointer."""
    model = resolve_model(config.models["default"])
    tools = aggregate_tools(config, sandbox, skills)
    prompt = _build_system_prompt(config, memory, skills)

    return create_react_agent(
        model,
        tools,
        prompt=prompt,
        checkpointer=MemorySaver(),
    )


def _build_system_prompt(
    config: AppConfig,
    memory: MemoryStore,
    skills: SkillLoader | None = None,
) -> str:
    sections = [_BASE_PROMPT]

    # Identity: NERV.md + SOUL.md + USER.md + language
    profile = load_profile(config.settings.language)
    if profile:
        sections.append(profile)

    # Conversational memory (facts)
    facts = memory.get_context()
    if facts:
        sections.append(facts)

    # Available skills
    if skills:
        fragment = skills.prompt_fragment()
        if fragment:
            sections.append(fragment)

    return "\n\n".join(sections)
