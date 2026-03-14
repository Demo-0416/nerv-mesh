# 060 执行架构设计 v1

## 核心模型：三层结构

```
┌─────────────────────────────────────────────────────┐
│                     DAG 层                          │
│              编排多个 sub-agent                     │
├─────────────────────────────────────────────────────┤
│  ┌─────────┐   ┌─────────┐   ┌─────────┐          │
│  │ Agent A │   │ Agent B │   │ Agent C │          │
│  │  ReAct  │   │  ReAct  │   │  ReAct  │          │
│  │  Loop   │   │  Loop   │   │  Loop   │          │
│  └─────────┘   └─────────┘   └─────────┘          │
└─────────────────────────────────────────────────────┘
```

| 层级 | 职责 | 触发条件 |
|-----|------|---------|
| **DAG** | 编排层，多 agent 协作调度 | 任务需要多 agent 协作 |
| **Agent** | 执行单元，封装特定能力 | DAG 节点 / 单 agent 任务 |
| **ReAct** | 决策循环，思考-行动-观察 | Agent 内部执行逻辑 |

**不存在"模式切换"**——ReAct 是 agent 的内部实现，DAG 是 agent 的编排方式。

## 两种执行模式

### Single 模式

单 agent 用 ReAct 循环完成任务。

```
用户：帮我重构 auth.py
    │
    ▼
判断：单 agent 可完成
    │
    ▼
Agent: refactor_agent (ReAct Loop)
    │
    ▼
完成
```

### Multi 模式

DAG 编排多 agent 并行/串行执行。

```
用户：分析这个项目的代码质量、安全漏洞、性能瓶颈
    │
    ▼
判断：需要多 agent 协作
    │
    ▼
生成 DAG:
    ┌────────────┬────────────┐
    │            │            │
    ▼            ▼            ▼
code_agent   security_agent  perf_agent
(ReAct)       (ReAct)        (ReAct)
    │            │            │
    └────────────┼────────────┘
                 │
                 ▼
           aggregator_agent
              (ReAct)
```

## 模式判断

由 Planner Agent 自动判断，不依赖用户手动选择。

```python
class TaskPlanner:
    async def plan(self, user_input: str) -> Plan:
        """
        输出两种结构之一：
        1. SingleAgentPlan：单个 agent 用 ReAct
        2. MultiAgentPlan：DAG 编排多个 agent
        """
        # 调用 LLM 判断
        # 规则：
        # - 单 agent 能完成 → single
        # - 需要多 agent 协作 → multi
```

## DAG 设计

### 节点类型

| 类型 | 说明 |
|-----|------|
| `agent` | 执行一个 sub-agent（内部 ReAct） |
| `tool` | 单次工具调用 |
| `human_review` | 等待人工确认 |
| `aggregator` | 汇总多个上游节点结果 |

### 边与条件

```json
{
  "from": "node_a",
  "to": "node_b",
  "condition": "success"  // success / failed / always
}
```

### 无环保证

动态生成 DAG 后，通过拓扑排序校验：

```python
def validate_dag(nodes: list, edges: list) -> bool:
    """拓扑排序检测环"""
    # 如果能完成拓扑排序 = 无环
```

## 存储设计

### 技术选型

**PostgreSQL 作为统一存储**

理由：
- 递归查询（WITH RECURSIVE）支持图遍历
- JSONB 支持复杂查询
- pgvector 扩展支持后续向量检索
- 事务保证 DAG 状态更新的原子性

### 数据模型

```sql
-- 任务
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    user_input TEXT,
    plan_type VARCHAR(20),      -- 'single' | 'multi'
    status VARCHAR(50),
    context JSONB,
    created_at TIMESTAMP
);

-- DAG 定义（multi 模式）
CREATE TABLE task_dags (
    id UUID PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    nodes JSONB,
    edges JSONB,
    created_at TIMESTAMP
);

-- Agent 执行记录
CREATE TABLE agent_runs (
    id UUID PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    dag_node_id VARCHAR(255),   -- multi 模式关联 DAG 节点
    agent_name VARCHAR(100),
    status VARCHAR(50),
    created_at TIMESTAMP
);

-- ReAct 步骤
CREATE TABLE react_steps (
    id UUID PRIMARY KEY,
    agent_run_id UUID REFERENCES agent_runs(id),
    step_num INT,
    thought TEXT,
    action VARCHAR(100),
    action_input JSONB,
    observation TEXT,
    created_at TIMESTAMP
);
```

## 执行流程

```python
class Executor:
    async def run(self, user_input: str) -> str:
        # 1. 规划
        plan = await self.planner.plan(user_input)

        # 2. 创建任务
        task_id = await self.db.create_task(user_input, plan.type)

        # 3. 执行
        if plan.type == 'single':
            return await self._run_single(task_id, plan.agent)
        else:
            return await self._run_multi(task_id, plan.dag)

    async def _run_single(self, task_id: str, agent_name: str) -> str:
        """单个 agent ReAct 循环"""
        # ...

    async def _run_multi(self, task_id: str, dag: DAG) -> str:
        """DAG 编排多 agent"""
        while not dag.is_completed():
            ready_nodes = dag.get_ready_nodes()
            await asyncio.gather(*[
                self._run_agent_node(task_id, node)
                for node in ready_nodes
            ])
```

## Checkpointing

支持 long-horizon 任务的暂停/恢复。

- **Single 模式**：checkpoint 存当前 ReAct 步骤 + 上下文
- **Multi 模式**：checkpoint 存所有 DAG 节点状态

## 开放问题

- DAG 动态修改：执行中途是否能调整 DAG 结构
- 子 agent 间通信：是否允许直接通信，还是只能通过 orchestrator
- 失败重试策略：节点级别的重试边界