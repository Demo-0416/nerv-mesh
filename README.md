# nerv-mesh

通用 AI 智能体，基于 LangGraph + LangChain 构建，支持多模型（阿里 Coding Plan）、多渠道（CLI / 飞书 / HTTP API），具备自我扩展能力。

## 架构

```
┌──────────────────────────────────────────────────────────┐
│  Channels          CLI · 飞书 Bot · HTTP Gateway         │
├──────────────────────────────────────────────────────────┤
│  Agent             LangGraph ReAct + Checkpoint          │
├──────────────────────────────────────────────────────────┤
│  Tools             Builtin · Meta(自省/自扩展) · MCP     │
├──────────────────────────────────────────────────────────┤
│  LLM               langchain-core 多模型路由             │
├──────────────────────────────────────────────────────────┤
│  Skills            SKILL.md 懒加载 · 内置 + 自定义       │
├──────────────────────────────────────────────────────────┤
│  Memory            JSON fact store · 上下文注入           │
├──────────────────────────────────────────────────────────┤
│  Sandbox           Local 隔离执行 · 超时控制              │
├──────────────────────────────────────────────────────────┤
│  Config            多文件配置 · 首次运行自动初始化         │
└──────────────────────────────────────────────────────────┘
```

## 应用与数据隔离

nerv-mesh 严格分离**应用代码**（不可变）和**用户数据**（可变）。

安装后，所有运行时数据统一存放在 `~/.nerv-mesh/`：

```
~/.nerv-mesh/                       ← 唯一的用户数据目录
├── config.yaml                     # 基础设施（sandbox、gateway）
├── models.yaml                     # LLM 模型配置（含 API Key）
├── mcp.json                        # MCP servers（兼容 Claude Desktop 格式）
├── settings.json                   # 用户偏好（memory、feishu、skills）
├── memory.json                     # 记忆存储
├── sandbox/                        # 沙箱工作目录
├── threads/                        # 对话线程
└── skills/
    └── custom/                     # agent 自己创建的 skills
```

首次运行时，`~/.nerv-mesh/` 自动创建并从内置模板初始化默认配置。

agent **不能**修改自己的源代码，只能操作 `~/.nerv-mesh/` 下的文件。

## 安装

### 前置要求

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) 包管理器

### 从源码安装（开发模式）

```bash
git clone <repo-url> nerv-mesh
cd nerv-mesh
uv sync --group dev
```

### 全局安装（推荐）

```bash
# 构建 wheel 包
uv build

# 全局安装
uv tool install dist/nerv_mesh-0.1.0-py3-none-any.whl

# 安装后可在任意位置使用
nerv-mesh
```

### 打包发布

```bash
# 构建 sdist + wheel
uv build

# 产出在 dist/ 目录
ls dist/
# nerv_mesh-0.1.0.tar.gz
# nerv_mesh-0.1.0-py3-none-any.whl
```

包内含 `_defaults/`（默认配置模板）和 `_builtin_skills/`（内置技能），随包一起分发。

## 启动方式

### 交互式 CLI

```bash
# 进入交互对话
nerv-mesh

# 或显式指定子命令
nerv-mesh chat
```

### 单次执行

```bash
nerv-mesh chat -p "帮我分析一下当前目录的代码结构"
```

### HTTP Gateway

```bash
# 启动 HTTP 网关（默认 0.0.0.0:8000）
nerv-mesh serve

# 指定端口
nerv-mesh serve --port 9000
```

Gateway 启动后可用的 API：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/chat` | POST | 同步对话 |
| `/api/chat/stream` | POST | SSE 流式对话 |
| `/api/config/models` | GET | 查看可用模型 |
| `/api/skills` | GET | 查看已安装 Skills |
| `/api/feishu/webhook` | POST | 飞书事件回调 |

调用示例：

```bash
curl http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'
```

### 飞书 Bot

1. 在[飞书开放平台](https://open.feishu.cn)创建应用
2. 编辑 `~/.nerv-mesh/settings.json`，填入飞书凭证
3. 启动 Gateway：`nerv-mesh serve`
4. 在飞书后台配置事件订阅地址：`https://<your-domain>/api/feishu/webhook`
5. 订阅 `im.message.receive_v1` 事件

## 配置

所有配置文件位于 `~/.nerv-mesh/`，按职责拆分，互不影响：

| 文件 | 职责 | 修改频率 |
|------|------|----------|
| `config.yaml` | 基础设施（sandbox 超时、gateway 端口） | 很少 |
| `models.yaml` | LLM 模型（provider、API Key、模型名） | 加模型时 |
| `mcp.json` | MCP 服务器（兼容 Claude Desktop 格式） | 加工具时 |
| `settings.json` | 用户偏好（memory、feishu、skills 目录） | 个性化 |

### 模型配置示例 (`models.yaml`)

```yaml
default:
  provider: "langchain_openai:ChatOpenAI"
  base_url: "https://coding.dashscope.aliyuncs.com/v1"
  api_key: "sk-sp-your-key"
  model: "MiniMax-M2.5"
  temperature: 0.7

reasoning:
  provider: "langchain_openai:ChatOpenAI"
  base_url: "https://coding.dashscope.aliyuncs.com/v1"
  api_key: "sk-sp-your-key"
  model: "kimi-k2.5"
  temperature: 0.3
```

### MCP 配置示例 (`mcp.json`)

格式与 Claude Desktop / Cursor 完全兼容，可直接复制已有配置：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "ghp_xxx" }
    }
  }
}
```

## Skills 系统

### 内置 Skills

随包发布，开箱即用：

- **research** — 深度研究，多角度搜索 + 交叉验证 + 结构化报告
- **code-review** — 代码审查，检查 bug、安全问题、风格一致性

### 自定义 Skills

agent 可以通过 `skill_create` 工具自己创建 skill，存放在 `~/.nerv-mesh/skills/custom/`：

```
~/.nerv-mesh/skills/custom/
└── daily-report/
    └── SKILL.md
```

SKILL.md 格式：

```markdown
---
name: daily-report
description: 根据 git log 生成每日工作总结
version: 0.1.0
---

## Instructions
...
```

也可以手动创建目录和 `SKILL.md`，重启后自动加载。

## 自我扩展能力

nerv-mesh 内置元工具，具备运行时自我扩展能力：

| 工具 | 功能 |
|------|------|
| `introspect` | 查看当前所有模型、工具、skills、MCP |
| `skill_create` | 创建新 skill |
| `skill_list` | 列出已安装 skills |
| `mcp_install` | 安装 MCP server（写入 mcp.json） |
| `mcp_list` | 列出已配置 MCP servers |
| `mcp_remove` | 移除 MCP server |

示例对话：

```
> 帮我安装一个 github 的 MCP server
→ MCP server 'github' installed. Restart gateway to activate.

> 帮我创建一个 daily-report 的 skill，用于生成每日工作总结
→ Skill 'daily-report' created at ~/.nerv-mesh/skills/custom/daily-report/SKILL.md
```

## 开发

```bash
# 安装开发依赖
uv sync --group dev

# 运行测试
uv run pytest

# 代码检查
uv run ruff check src/ tests/

# 从源码启动（开发模式）
uv run nerv-mesh
```

## 技术栈

| 组件 | 技术 |
|------|------|
| Agent 编排 | LangGraph 1.x |
| 模型抽象 | LangChain Core |
| 配置校验 | Pydantic 2 |
| HTTP Gateway | FastAPI + Uvicorn |
| 飞书集成 | lark-oapi |
| CLI 输出 | Rich |
| 包管理 | uv + Hatchling |
