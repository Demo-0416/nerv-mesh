# 001 OpenClaw Overview

## 调研元数据

- 调研日期：2026-03-01
- 信息来源：GitHub README, 官方文档
- 版本/提交：v2025.x (持续活跃开发)

## 项目概览

**定位**：个人 AI 助手（Personal AI Assistant），运行在用户自有设备上。

**基本信息**：
- GitHub: https://github.com/openclaw/openclaw
- Stars: 242,084
- Forks: 46,776
- 创建时间：2025-11-24
- License: MIT

## 核心特性

1. **多渠道接入**：支持 WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage (BlueBubbles), Microsoft Teams, Matrix, Zalo, WebChat
2. **多平台客户端**：macOS 菜单栏应用、iOS/Android 节点、macOS/iOS/Android 全平台支持
3. **Voice + Canvas**：Voice Wake 语音唤醒、Talk Mode 语音对话、Live Canvas 可视化工作空间
4. **本地优先 Gateway**：单一控制平面，管理 sessions、channels、tools、events
5. **安全设计**：DM 配对机制、allowlist 控制、敏感输入隔离

## 架构组件

- **Gateway**：WS 控制平面 (ws://127.0.0.1:18789)，CLI 表面
- **Pi Agent Runtime**：RPC 模式，tool streaming + block streaming
- **Session Model**：main session、group 隔离、activation modes、queue modes
- **Media Pipeline**：图像/音频/视频处理、转录 hooks、临时文件生命周期

## 对 nerv-mesh 的启发

- **多渠道架构**：Gateway 模式解耦 agent 与渠道，可借鉴用于 nerv-mesh 的 channel abstraction
- **Session 模型**：group 隔离、activation modes、reply-back 机制可参考
- **安全设计**：DM pairing + allowlist 策略，适合需要安全隔离的场景
- **本地优先**：强调设备本地运行，数据不外传，适合 privacy-first 的 agent 设计
