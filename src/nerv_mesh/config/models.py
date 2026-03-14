"""Configuration data models — split across multiple config files.

File layout:
  config.yaml    → Infra (sandbox, gateway, tools)
  models.yaml    → LLM providers
  mcp.json       → MCP servers (Claude Desktop / Cursor compatible)
  settings.json  → User prefs (memory, feishu, skills, defaults)
"""

from pydantic import BaseModel, Field

# ── models.yaml ───────────────────────────────────────────────────────────

class ModelConfig(BaseModel):
    """A single LLM provider configuration."""

    provider: str = "langchain_openai:ChatOpenAI"
    base_url: str | None = None
    api_key: str | None = None
    model: str
    temperature: float = 0.7
    max_tokens: int | None = None
    tags: list[str] = Field(default_factory=list)


# ── config.yaml (infra) ──────────────────────────────────────────────────

class SandboxConfig(BaseModel):
    """Sandbox execution settings."""

    mode: str = "local"
    timeout: int = 30


class GatewayConfig(BaseModel):
    """HTTP gateway settings."""

    host: str = "0.0.0.0"
    port: int = 8000


class ToolRef(BaseModel):
    """Reference to a tool implementation."""

    name: str
    use: str  # "module.path:function_name"
    enabled: bool = True


# ── mcp.json ──────────────────────────────────────────────────────────────

class McpServerConfig(BaseModel):
    """A single MCP server — Claude Desktop / Cursor compatible format."""

    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    enabled: bool = True


class McpConfig(BaseModel):
    """Contents of mcp.json."""

    mcpServers: dict[str, McpServerConfig] = Field(default_factory=dict)


# ── settings.json ─────────────────────────────────────────────────────────

class MemoryConfig(BaseModel):
    """Memory system settings."""

    enabled: bool = True
    max_facts: int = 50
    inject_limit: int = 15


class FeishuConfig(BaseModel):
    """Feishu bot credentials."""

    app_id: str = ""
    app_secret: str = ""
    encrypt_key: str = ""
    verification_token: str = ""


class SkillsConfig(BaseModel):
    """Skill discovery settings."""

    dirs: list[str] = Field(default_factory=lambda: ["skills/builtin", "skills/custom"])


class Settings(BaseModel):
    """Contents of settings.json — user preferences and channel configs."""

    default_model: str = "default"
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    feishu: FeishuConfig = Field(default_factory=FeishuConfig)
    skills: SkillsConfig = Field(default_factory=SkillsConfig)


# ── Assembled AppConfig ──────────────────────────────────────────────────

class AppConfig(BaseModel):
    """Assembled from config.yaml + models.yaml + mcp.json + settings.json."""

    models: dict[str, ModelConfig]
    sandbox: SandboxConfig = Field(default_factory=SandboxConfig)
    gateway: GatewayConfig = Field(default_factory=GatewayConfig)
    tools: list[ToolRef] = Field(default_factory=list)
    mcp: McpConfig = Field(default_factory=McpConfig)
    settings: Settings = Field(default_factory=Settings)

    @property
    def memory(self) -> MemoryConfig:
        return self.settings.memory

    @property
    def feishu(self) -> FeishuConfig:
        return self.settings.feishu

    @property
    def skills_config(self) -> SkillsConfig:
        return self.settings.skills
