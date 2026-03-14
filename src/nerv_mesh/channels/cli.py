"""Interactive CLI channel — streaming ReAct agent in the terminal."""

import uuid

from langchain_core.messages import AIMessageChunk, HumanMessage
from rich.console import Console
from rich.theme import Theme

from nerv_mesh.agents import build_agent
from nerv_mesh.config.models import AppConfig
from nerv_mesh.memory import MemoryStore
from nerv_mesh.sandbox import LocalSandbox
from nerv_mesh.skills import SkillLoader

_theme = Theme({"prompt": "bold green", "tool": "dim cyan", "error": "bold red"})
console = Console(theme=_theme)


async def run_cli(config: AppConfig) -> None:
    """Start an interactive REPL backed by the agent graph."""
    sandbox, memory, agent = _init_components(config)
    thread_id = str(uuid.uuid4())

    _print_banner()

    while True:
        try:
            user_input = console.input("[prompt]nerv-mesh>[/prompt] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nBye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            console.print("Bye!")
            break

        await _process_turn(agent, user_input, thread_id)


async def _process_turn(agent, user_input: str, thread_id: str) -> None:
    """Stream one user → agent turn."""
    run_config = {"configurable": {"thread_id": thread_id}}
    input_msg = {"messages": [HumanMessage(content=user_input)]}

    async for event in agent.astream_events(input_msg, config=run_config, version="v2"):
        _handle_event(event)

    console.print()  # newline after streamed output


def _handle_event(event: dict) -> None:
    """Route a single stream event to the appropriate printer."""
    kind = event["event"]

    if kind == "on_chat_model_stream":
        chunk = event["data"].get("chunk")
        if isinstance(chunk, AIMessageChunk) and chunk.content:
            console.print(chunk.content, end="")

    elif kind == "on_tool_start":
        name = event.get("name", "?")
        console.print(f"\n[tool]  {name}[/tool]", end="")

    elif kind == "on_tool_end":
        output = event["data"].get("output", "")
        _print_tool_output(str(output))


def _print_tool_output(output: str, max_lines: int = 10) -> None:
    """Show truncated tool output."""
    lines = output.strip().splitlines()
    preview = lines[:max_lines]
    console.print()
    for line in preview:
        console.print(f"[dim]  {line}[/dim]")
    if len(lines) > max_lines:
        console.print(f"[dim]  ... ({len(lines) - max_lines} more lines)[/dim]")


def _init_components(config: AppConfig):
    from nerv_mesh.config.paths import home_dir

    h = home_dir()
    sandbox = LocalSandbox(workdir=h / "sandbox", timeout=config.sandbox.timeout)
    memory = MemoryStore(
        path=h / "memory.json",
        max_facts=config.memory.max_facts,
        inject_limit=config.memory.inject_limit,
    )
    skills = SkillLoader(config.skills_config.dirs)
    agent = build_agent(config, sandbox, memory, skills)
    return sandbox, memory, agent


def _print_banner() -> None:
    console.print("[bold]nerv-mesh[/bold] v0.1.0 — General-Purpose AI Agent")
    console.print("Type [bold]exit[/bold] to quit.\n")
