"""Shared runtime dependencies for the gateway."""

from dataclasses import dataclass, field

from langgraph.graph.state import CompiledStateGraph

from nerv_mesh.agents import build_agent
from nerv_mesh.config.models import AppConfig
from nerv_mesh.memory import MemoryStore
from nerv_mesh.sandbox import LocalSandbox
from nerv_mesh.skills import SkillLoader


@dataclass
class Runtime:
    """Holds all long-lived objects shared across gateway routes."""

    config: AppConfig
    sandbox: LocalSandbox
    memory: MemoryStore
    skills: SkillLoader
    agent: CompiledStateGraph = field(init=False)

    def __post_init__(self) -> None:
        self.agent = build_agent(self.config, self.sandbox, self.memory, self.skills)


def create_runtime(config: AppConfig) -> Runtime:
    """Assemble the runtime from config."""
    from nerv_mesh.config.paths import home_dir

    h = home_dir()
    return Runtime(
        config=config,
        sandbox=LocalSandbox(workdir=h / "sandbox", timeout=config.sandbox.timeout),
        memory=MemoryStore(
            path=h / "memory.json",
            max_facts=config.memory.max_facts,
            inject_limit=config.memory.inject_limit,
        ),
        skills=SkillLoader(config.skills_config.dirs),
    )
