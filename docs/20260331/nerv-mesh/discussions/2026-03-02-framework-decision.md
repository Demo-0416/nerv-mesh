# 讨论记录：2026-03-02 框架选择与工具调用机制

## 参与者

- Xingyu
- Claude

## 讨论议题

1. 框架选择：LangGraph vs 自建
2. DeerFlow 框架分析
3. 工具调用机制（Tool Calling）
4. 跨模型适配方案

## 关键结论

### 框架选择：自建，不使用 LangGraph

**原因**：
- LangGraph 有学习成本
- nerv-mesh 的 memory 机制（突触网络）是自定义算法，框架不一定适配
- 保持对核心逻辑的完全控制

**参考 DeerFlow 的分层思路，但不依赖 LangGraph**。

### DeerFlow 框架分析

**LangChain Core vs LangGraph 职责分离**：

| 组件 | 职责 |
|-----|------|
| **LangChain Core** | 跨模型 Function Calling 适配、模型调用抽象 |
| **LangGraph** | 状态管理、图编排、Checkpointing、Middleware |

**关键发现**：
- DeerFlow 用 `langchain-core` 的 `resolve_class()` 动态加载模型类
- `create_agent()` 使用 LangChain 的 agent 创建方法
- 工具通过配置文件声明，`get_available_tools()` 动态加载
- LangGraph 的核心是 `StateGraph`，提供状态管理和图执行

**DeerFlow 的 DAG 生成**：
- 不是动态生成 DAG，而是预定义的图结构
- 通过 middleware 控制行为
- 工具（包括 subagent 工具）在 agent 初始化时注入

### 工具调用机制

**核心问题**：Agent 如何"主动"调用工具？

**两种实现方式**：

| 方式 | 原理 | 优点 | 缺点 |
|-----|------|------|------|
| **Prompt 格式** | LLM 输出特定格式文本，系统解析 | 通用，不依赖模型能力 | 需要解析逻辑，不够精确 |
| **原生 Function Calling** | LLM 输出结构化调用意图 | 精确，原生支持 | 依赖模型能力，各厂实现不同 |

**流程**：
```
用户输入 → LLM 思考 → 输出结构化意图（function call）→ 系统解析 → 执行工具 → 返回结果 → LLM 继续思考
```

**DeerFlow 实现参考**：
```python
# deer-flow/backend/src/tools/tools.py
def get_available_tools(groups, include_mcp, model_name, subagent_enabled):
    loaded_tools = [resolve_variable(tool.use, BaseTool) for tool in config.tools...]
    mcp_tools = get_cached_mcp_tools() if include_mcp else []
    return loaded_tools + builtin_tools + mcp_tools
```

### 跨模型适配方案

**三个选项**：

| 方案 | 描述 | 工作量 | 灵活性 |
|-----|------|--------|--------|
| **A. 最小依赖 LangChain** | 仅用 `langchain-core` 的模型适配层 | 中 | 高 |
| **B. 完全自建** | 自己实现各模型的适配器 | 高 | 最高 |
| **C. 完整 LangChain+LangGraph** | 全栈使用框架 | 低 | 低 |

**建议**：方案 A 或 B，保持核心控制权。

## 架构决策总结

```
┌─────────────────────────────────────────────────────────┐
│                    nerv-mesh 架构                        │
├─────────────────────────────────────────────────────────┤
│  DAG 层        │ 自建，PostgreSQL 存储                   │
│  Agent 层      │ 自建，ReAct 循环                        │
│  工具层        │ 统一接口，支持 Tools/Skills/MCP         │
│  模型适配层    │ 待定：langchain-core 或自建            │
│  存储层        │ PostgreSQL（DAG + 突触网络 + 状态）     │
└─────────────────────────────────────────────────────────┘
```

## 遗留问题

- [ ] 模型适配层最终决策：langchain-core vs 自建
- [ ] DAG 动态生成 vs 预定义模板
- [ ] 工具注册与发现机制

## 相关文档

- [060-执行架构设计 v1](../design/060-execution-architecture-v1.md)
- [2026-03-01 执行架构讨论](./2026-03-01-execution-architecture.md)
- [DeerFlow 研究](../../research/deerflow-2.0/README.md)