# 讨论记录：2026-03-01 Model Config

## 新增需求

- 需要支持统一的 model 配置功能
- 需要覆盖 `coding plan` 场景
- 需要支持多 API 提供商接入

## 结论（当前）

1. 在系统架构中新增 `Model Config Layer`
2. 增加 `050-model-config-routing-v0.md` 作为专题设计文档
3. 路线图纳入 model config 的阶段目标（M1 基础版、M3 多 provider 版）

## 下一步问题

1. 第一批 provider 清单（至少 2 个）怎么选
2. `coding_plan` 的最终结构化 schema 是否需要版本号
3. 路由策略先走规则引擎还是直接做可学习策略
