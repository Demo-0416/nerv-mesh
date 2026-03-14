# 040 里程碑路线图 v0

## M0：文档先行（当前）

- 完成愿景、架构、memory 机制、子代理与工具设计文档
- 定义术语表与决策记录流程

## M1：最小可运行骨架

- 单进程 orchestrator
- 至少 2 个子代理
- 1 个 channel（CLI 或飞书 mock）
- 受限 sandbox tool
- 基础记忆图（节点+边+权重）
- 基础 model config（单 provider + 角色路由）

## M2：睡眠/做梦机制

- 支持定时 sleep cycle
- 具备记忆巩固/衰减
- 生成并管理 hypothesis（梦境）节点

## M3：多渠道与工具扩展

- 飞书真实接入
- function calling 与 MCP 对接
- skills 工作流接入统一 registry
- 多 provider 模型配置与 fallback 策略
- coding plan 专用模型 profile 与结构化输出

## M4：评估与稳态

- 长周期任务成功率指标
- 记忆质量指标（命中率、污染率、遗忘收益）
- 安全与审计基线
