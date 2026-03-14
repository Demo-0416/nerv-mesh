# 讨论记录：2026-03-01 文档复盘与挑战问题

## 复盘范围

- `design/025-memory-architecture-v1.md`
- `design/060-execution-architecture-v1.md`
- `design/010-system-architecture-v0.md`
- `design/040-roadmap-v0.md`
- `research/*`

## 新增细节（相比早期版本）

1. memory 从“突触图抽象”落地为 `Key-Memory` 检索机制（表层 Key + 深层抽象）
2. 执行架构明确为三层：`DAG 编排` / `Agent 执行单元` / `ReAct 决策循环`
3. 存储策略明确：`M1 SQLite`，`M2+ PostgreSQL(+JSONB/+pgvector)`
4. 明确了“优先自建执行框架，不直接依赖 LangGraph”

## 挑战问题（建议你尽快拍板）

### 1) Memory 路线冲突：Key-Memory vs 突触网络

当前 `025` 以 key 检索为主，和愿景中的“巨大神经突触网络”还不是同一层次。

需要决策：
- Key-Memory 是最终方案，还是仅作为 v1 检索前端？
- 如果是前端，后端突触图的最小实体关系何时定义（node/edge/weight/update rule）？

### 2) 版本命名不一致

- 文件名：`025-memory-architecture-v1.md`
- 标题：`Memory 架构设计 v2`

需要决策：统一为 v1 还是 v2，避免后续 ADR 和实现引用混乱。

### 3) “不用 LangGraph”与“long-horizon 稳定性”之间的工程代价

你选择自建是合理的，但代价是要自己补齐：
- durable execution
- checkpoint/replay
- failure recovery
- traceability

需要决策：
- 完全自建，还是保留“可插拔编排后端”抽象（先自建，后续可接 LangGraph/Temporal）？

### 4) Single/Multi 判定策略的可解释性

文档里由 Planner 自动判定 single/multi，但缺少可审计规则。

需要决策：
- 是否先做规则优先（复杂度阈值、并行收益阈值）再引入 LLM 判定？
- 判定结果是否必须产出理由（reason code）写入数据库？

### 5) 调研数据可信度与更新机制

`research/openclaw/001-overview.md` 中 stars/forks 等数据会快速过期。

需要决策：
- 调研文档是否加“数据刷新日期 + 抓取方式 + 可信级别”字段？
- 是否区分“稳定结论”和“波动指标”？

## 建议的下一步

1. 新增一个 ADR：`ADR-001-memory-v1-boundary.md`，明确 Key-Memory 与突触图边界
2. 新增一个 ADR：`ADR-002-execution-backend-strategy.md`，明确自建与可插拔策略
3. 新增一个 schema 文档：`coding-plan.schema.json`（先文档化，不实现）
