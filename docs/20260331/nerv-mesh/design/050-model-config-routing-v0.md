# 050 Model 配置与路由设计 v0

## 目标

为 `nerv-mesh` 增加统一的模型配置中心，支持：

- 多模型/多提供商配置（不同 API）
- 按任务类型和子代理角色路由模型
- `coding plan` 生成与执行阶段的模型解耦
- 与 tools（function calling / MCP / skills）能力匹配

## 核心概念

- `Provider`: 模型提供商（OpenAI-compatible、Anthropic、Gemini、Qwen 等）
- `Model Profile`: 某个模型在系统中的可执行配置快照
- `Routing Policy`: 从任务上下文选择 Model Profile 的规则
- `Capability Matrix`: 模型能力矩阵（function calling、json schema、streaming 等）

## Model Profile（建议字段）

- `id`: profile 唯一标识
- `provider`: 提供商标识
- `api.base_url`: API 地址
- `api.auth_env`: 密钥环境变量名（不在配置中存明文密钥）
- `model`: 具体模型名称
- `generation`: `temperature`、`top_p`、`max_tokens`
- `limits`: 超时、重试、并发、预算上限
- `capabilities`: 是否支持 function calling、json schema、vision、streaming
- `tags`: 用于路由筛选（如 `planner`、`coder`、`low-cost`、`high-reasoning`）
- `status`: `active` / `disabled` / `canary`

## Routing Policy（建议）

1. 首选按 `agent role` 路由：
   - `Planner Agent` -> 高推理模型
   - `Execution/Coder Agent` -> 代码能力强且 function calling 稳定的模型
   - `Verifier Agent` -> 低温度、高一致性模型
2. 再按 `task type` 细分：
   - `coding_plan`、`code_generation`、`api_calling`、`memory_summarization`
3. 加预算守卫：
   - 超预算时自动降级到低成本 profile
4. 失败回退：
   - 主 profile 失败 -> fallback profile -> 人工确认

## Coding Plan 支持（提案）

`coding plan` 不是自由文本，建议定义结构化输出：

- `goal`: 目标
- `constraints`: 约束
- `steps`: 可执行步骤列表
- `risks`: 风险与回滚点
- `verification`: 验证方法与验收标准

流程：

1. Planner 选择 `coding_plan` profile 产出结构化计划
2. Verifier 检查计划完整性
3. Execution Agent 按计划执行并回写状态
4. Memory 记录计划与执行偏差，用于下一轮路由优化

## API 兼容策略（提案）

- 优先支持 `OpenAI-compatible API` 抽象层，降低接入成本
- 为非兼容提供商保留 adapter（字段映射 + 错误码映射）
- 所有 provider 统一返回系统内部的 `NormalizedResponse` 结构

## 与现有模块的关系

- `orchestrator`：请求模型路由并执行
- `subagents`：基于 role 绑定默认 profile
- `tools`：依据模型能力决定调用策略（原生 function calling 或文本协议）
- `memory`：记录模型选择与结果质量，反馈给路由策略

## v1 范围建议

- 支持 2-3 个 provider
- 支持 role + task type 路由
- 支持 fallback 与预算守卫
- 支持 `coding_plan` 结构化输出

## 开放问题

- 路由策略是规则优先还是引入学习型策略（bandit/RL）
- 是否需要 tenant 级隔离配置
- 不同 provider 的速率限制如何统一编排
