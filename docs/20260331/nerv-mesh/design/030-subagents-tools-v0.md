# 030 Sub-Agents 与 Tools 设计 v0

## Sub-Agents 角色建议

- `Planner Agent`：拆解 long-horizon 目标，维护计划树
- `Research Agent`：信息检索、知识整合
- `Execution Agent`：调用工具执行具体动作
- `Verifier Agent`：结果校验、风险审查
- `Memory Curator Agent`：记忆写入、清理与标签治理

## 调度策略（初版）

- 主代理负责全局目标与优先级
- 子代理领取任务时附带：上下文片段、预算、截止时间
- 每个子任务需要：输入契约、输出契约、失败回退策略

## Tools 统一接口（概念）

- `Skill Tool`：复用本地 skill 工作流
- `Function Tool`：标准 schema 函数调用
- `MCP Tool`：通过 MCP server 暴露能力
- `Sandboxed Shell Tool`：受限命令执行

## 飞书接入（初版）

- 入站：消息事件 -> 任务请求
- 出站：阶段进度、结果摘要、需要人工决策的问题
- 约束：敏感操作需二次确认

## 开放问题

- 子代理间是否允许直接通信
- 工具错误分类（可重试 / 不可重试 / 需人工）
- 不同渠道输入的上下文规范化格式
