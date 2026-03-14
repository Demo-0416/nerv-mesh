# 010 系统架构 v0

## 总体分层

1. `Channel Layer`：消息入口与输出（飞书优先）
2. `Orchestration Layer`：主代理、任务编排、子代理调度
3. `Model Config Layer`：多模型配置、能力矩阵、路由策略
4. `Execution Layer`：sandbox + tools 执行
5. `Memory Layer`：突触图谱、睡眠巩固、梦境生成
6. `Observability Layer`：日志、轨迹、评估指标

## 核心数据流

1. 用户请求从 channel 进入
2. orchestrator 解析目标并形成 long-horizon plan
3. model config layer 根据角色/任务类型选择模型 profile
4. plan 分解为子任务并派发给 sub-agents
5. sub-agents 通过 tools 执行（受 sandbox 约束）
6. 执行结果写入 memory（形成/强化突触）
7. 定时触发 sleep cycle：巩固、抽象、衰减、梦境
8. 下一轮任务从 memory 检索上下文并继续推进

## 建议模块边界

- `nerv_mesh/channels/*`
- `nerv_mesh/orchestrator/*`
- `nerv_mesh/model_config/*`
- `nerv_mesh/subagents/*`
- `nerv_mesh/tools/*`
- `nerv_mesh/sandbox/*`
- `nerv_mesh/memory/*`
- `nerv_mesh/observability/*`

## 开放问题

- 主代理与子代理的状态同步策略（pull / push / event bus）
- 工具执行的幂等性与重试边界
- memory 写入是否需要“事实层 vs 推理层”分仓
- 模型路由策略的规则边界（固定规则 / 动态学习）
