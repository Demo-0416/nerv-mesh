# 讨论记录：2026-03-01 执行架构与存储

## 参与者

- Xingyu
- Claude

## 讨论议题

1. 存储技术选型
2. 是否使用 LangGraph 框架
3. DAG vs ReAct 模式
4. 执行架构设计

## 关键结论

### 存储：PostgreSQL

- 统一存储：DAG + 突触网络 + 任务状态
- 理由：递归查询支持图遍历、JSONB、pgvector 扩展、事务保证
- M1 可用 SQLite 快速验证，M2+ 切换 PostgreSQL

### 框架：自建，不用 LangGraph

- LangGraph 有学习成本
- nerv-mesh 的 memory 机制（突触网络）是自定义算法，框架不一定适配
- 保持对核心逻辑的完全控制

### DAG vs ReAct：不是二选一

**核心洞察**：DAG 和 ReAct 是不同层级的东西

| 层级 | 职责 |
|-----|------|
| DAG | 编排层，多 agent 协作调度 |
| Agent | 执行单元，封装特定能力 |
| ReAct | 决策循环，Agent 内部执行逻辑 |

- ReAct 是 agent 的内部实现
- DAG 是 agent 的编排方式
- **不存在"模式切换"问题**

### 执行架构：三层模型

```
DAG 层（编排）
    │
    └── Agent 层（执行单元）
            │
            └── ReAct 层（决策循环）
```

**两种执行模式**：
- Single：单 agent ReAct 完成
- Multi：DAG 编排多 agent

**模式判断**：Planner Agent 自动判断，不需要用户选择

## 遗留问题

- DAG 动态修改：执行中途是否能调整
- 子 agent 间通信方式
- 失败重试策略

## 产出文档

- [060-执行架构设计 v1](../design/060-execution-architecture-v1.md)