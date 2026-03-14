# 001 DeerFlow2.0 Overview

## 调研元数据

- 调研日期：2026-03-01
- 信息来源：GitHub README, 官方文档
- 版本/提交：v2.0 (2026-02-28 GitHub Trending #1)

## 项目概览

**定位**：超级 Agent Harness，编排 sub-agents、memory、sandboxes 执行复杂任务。

**基本信息**：
- GitHub: https://github.com/bytedance/deer-flow
- Stars: 22,790
- Forks: 2,733
- 创建时间：2025-05-07
- License: MIT
- 官方站点：https://deerflow.tech/

## 核心定位演变

DeerFlow 起源于 Deep Research 框架，社区将其扩展用于：
- 数据管道构建
- PPT/幻灯片生成
- Dashboard 启动
- 内容工作流自动化

2.0 版本从零重写，基于 **LangGraph + LangChain**，不再只是一个研究工具，而是一个完整的超级 agent harness。

## 核心特性

1. **Skills & Tools**：结构化能力模块，Markdown 定义工作流，按需加载支持长时间上下文
2. **Sub-Agents**：复杂任务分解，多 agent 协作
3. **Sandbox**：隔离执行环境，支持 Local/Docker/Kubernetes 三种模式
4. **Context Engineering**：上下文工程优化
5. **Long-Term Memory**：长期记忆能力
6. **MCP Server**：支持自定义 MCP servers 和 skills 扩展

## 架构组件

- **Backend**：LangGraph/LangChain 驱动
- **Frontend**：Web UI
- **Sandbox**：隔离执行环境
- **Provisioner**：Kubernetes 模式下的 pod 管理

## 对 nerv-mesh 的启发

- **Harness 架构**：从纯 research 框架演进为通用 harness，说明"可扩展性"是关键设计目标
- **Skills 机制**：Markdown 定义 + 按需加载，适合长时间运行的 agent
- **Sandbox 隔离**：Local/Docker/Kubernetes 三级隔离方案，安全与灵活性兼顾
- **Sub-agents 编排**：复杂任务分解模式，可用于 nerv-mesh 的任务分片
- **LangGraph 集成**：状态流管理、checkpointing 等特性值得参考
