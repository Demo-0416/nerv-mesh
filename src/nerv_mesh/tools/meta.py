"""Meta-tools — let the agent inspect and extend itself.

These tools give nerv-mesh self-evolution capabilities:
- Introspect: know what tools/skills/models are available
- Skill create: write new skills
- MCP manage: install/list/remove MCP servers
"""

import json

from langchain_core.tools import BaseTool, tool

from nerv_mesh.config.models import AppConfig, McpServerConfig
from nerv_mesh.config.paths import home_dir
from nerv_mesh.skills import SkillLoader


def make_meta_tools(config: AppConfig, skills: SkillLoader) -> list[BaseTool]:
    """Create meta-tools with access to runtime config."""
    return [
        _make_introspect(config, skills),
        _make_skill_create(),
        _make_skill_list(skills),
        _make_mcp_install(config),
        _make_mcp_list(config),
        _make_mcp_remove(config),
    ]


def _make_introspect(config: AppConfig, skills: SkillLoader) -> BaseTool:
    @tool
    def introspect() -> str:
        """Show all current capabilities: models, tools, skills, and MCP servers."""
        sections = []

        models = [f"  - {k}: {v.model} ({v.provider})" for k, v in config.models.items()]
        sections.append("Models:\n" + "\n".join(models))

        mcp = config.mcp.mcpServers
        if mcp:
            servers = [f"  - {k}: {v.command} {' '.join(v.args)}" for k, v in mcp.items()]
            sections.append("MCP Servers:\n" + "\n".join(servers))
        else:
            sections.append("MCP Servers: (none)")

        skill_list = skills.list_skills()
        if skill_list:
            sk = [f"  - {s['name']}: {s['description']}" for s in skill_list]
            sections.append("Skills:\n" + "\n".join(sk))
        else:
            sections.append("Skills: (none)")

        return "\n\n".join(sections)

    return introspect


def _make_skill_create() -> BaseTool:
    @tool
    def skill_create(name: str, description: str, instructions: str) -> str:
        """Create a new custom skill in ~/.nerv-mesh/skills/custom/<name>/."""
        skill_dir = home_dir() / "skills" / "custom" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        content = f"---\nname: {name}\ndescription: {description}\nversion: 0.1.0\n---\n\n"
        content += instructions
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
        return f"Skill '{name}' created at {skill_dir}/SKILL.md. Restart to activate."

    return skill_create


def _make_skill_list(skills: SkillLoader) -> BaseTool:
    @tool
    def skill_list() -> str:
        """List all installed skills with their descriptions."""
        items = skills.list_skills()
        if not items:
            return "No skills installed."
        lines = [f"- {s['name']} (v{s['version']}): {s['description']}" for s in items]
        return "\n".join(lines)

    return skill_list


def _make_mcp_install(config: AppConfig) -> BaseTool:
    @tool
    def mcp_install(
        name: str, command: str, cmd_args: str = "", env_json: str = "{}"
    ) -> str:
        """Install an MCP server by adding it to mcp.json.

        Args:
            name: Server name (e.g. "github", "filesystem")
            command: Command to run (e.g. "npx", "uvx")
            cmd_args: Space-separated arguments (e.g. "-y @modelcontextprotocol/server-github")
            env_json: JSON string of environment variables (e.g. '{"GITHUB_TOKEN": "ghp_xxx"}')
        """
        args_list = cmd_args.split() if cmd_args else []
        env_dict = json.loads(env_json) if env_json != "{}" else {}
        server = McpServerConfig(command=command, args=args_list, env=env_dict)

        mcp_path = home_dir() / "mcp.json"
        data = json.loads(mcp_path.read_text()) if mcp_path.exists() else {"mcpServers": {}}
        data["mcpServers"][name] = server.model_dump()
        mcp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

        return f"MCP server '{name}' installed. Restart gateway to activate."

    return mcp_install


def _make_mcp_list(config: AppConfig) -> BaseTool:
    @tool
    def mcp_list() -> str:
        """List all configured MCP servers from mcp.json."""
        servers = config.mcp.mcpServers
        if not servers:
            return "No MCP servers configured."
        lines = []
        for name, s in servers.items():
            status = "enabled" if s.enabled else "disabled"
            lines.append(f"- {name} [{status}]: {s.command} {' '.join(s.args)}")
        return "\n".join(lines)

    return mcp_list


def _make_mcp_remove(config: AppConfig) -> BaseTool:
    @tool
    def mcp_remove(name: str) -> str:
        """Remove an MCP server from mcp.json."""
        mcp_path = home_dir() / "mcp.json"
        if not mcp_path.exists():
            return "No mcp.json found."
        data = json.loads(mcp_path.read_text())
        if name not in data.get("mcpServers", {}):
            return f"MCP server '{name}' not found."
        del data["mcpServers"][name]
        mcp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return f"MCP server '{name}' removed."

    return mcp_remove
