# 025 Memory 架构设计 v2（最终版）

> 基于 2026-03-01 讨论整合
> 状态：最终版，不再变更

## 成为最终版的理由

### 核心创新：Double-Key-Memory

| 创新点 | 说明 |
|-------|------|
| **表层 Key** | 具体标签，"安全"、"API"、"权限" |
| **深层 Key** | 抽象类型，"复杂后端逻辑"、"系统设计" |
| **自然语言注入** | "之前我做 xxx 的时候"而非 XML 标签 |

这打破了传统 agent 的"语义匹配"模式，变成"专家经验检索"——遇到任务类型 → 加载对应经验 → 像专家一样思考。

### 什么是"非关键"

- ~~梦境机制~~：不是创新点，只是锦上添花
- ~~在线裁剪实验~~：过度设计
- ~~复杂权重系统~~：可以用简单的热度统计替代

### 设计原则

"像人一样思考"：
- 遇到任务 → 识别类型（Key 提取）
- 处理这类问题 → 调用经验（Memory 检索）
- 自然语言注入 → 让 agent"感受到"是经验而非数据

## 核心创新

**Key-Memory 检索**：打破传统语义匹配，更像人类专家思维

| 传统方式 | 你的设计 |
|---------|---------|
| 文本 → 向量相似度 | 任务类型 → Key → 专家经验 |
| "像不像" | "需不需要" |

---

## 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Memory System                         │
├─────────────────────────────────────────────────────────┤
│  Crystal Layer (始终加载)                                 │
│  ├── system_prompt                                       │
│  ├── agent_identity (SOUL.md)                           │
│  ├── user_profile (USER.md)                             │
│  └── core_skills                                        │
├─────────────────────────────────────────────────────────┤
│  Fluid Layer (动态)                                      │
│  ├── Key-Memory 索引 (HashMap: key → memory)            │
│  ├── 双层 Key：表层 + 深层                                │
│  └── 自然语言注入                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 1. 数据模型

### 1.1 Memory Node

```python
class MemoryNode:
    id: str

    # 事情是什么（场景/背景）
    scenario: str

    # Memory 核心（核心要点）
    core: str

    # Key（标签，用于检索）
    keys: list[str]

    # 深层抽象类型（可选）
    abstraction: str = None  # "复杂后端逻辑", "系统设计", "抽象理论讨论"

    # 元信息
    node_type: str        # "event" | "fact" | "hypothesis" | "framework"
    confidence: float
    created_at: datetime
```

### 1.2 Key 索引

```python
class KeyMemoryIndex:
    """Key → Memory 映射索引"""

    # key → memory_ids
    index: dict[str, set[str]]

    def query(self, keys: list[str]) -> list[str]:
        """根据 key 列表找到所有相关 memory"""
        result = set()
        for key in keys:
            result.update(self.index.get(key, set()))
        return list(result)
```

---

## 2. 检索流程

```
用户请求
    ↓
┌──────────────────────────────────────┐
│ Key 提取                              │
│   表层 Key：["安全", "API", "权限"]    │
│   深层 Key："复杂后端逻辑"             │
└──────────────────────────────────────┘
    ↓
Key 索引 O(1) 查找 → 拉取 Memory
    ↓
┌──────────────────────────────────────┐
│ 表层 Memory：具体经验                 │
│  场景 + 核心                          │
│ 深层 Memory：思维框架                 │
│ 抽象类型 + 思考方式                   │
└──────────────────────────────────────┘
    ↓
自然语言注入 → 执行
```

---

## 3. 双层 Key 设计

### 3.1 表层 Key

具体标签，直接匹配：

| 任务 | 表层 Key |
|-----|---------|
| 修改权限 | "安全"、"权限"、"数据一致性" |
| 用户支付 | "支付"、"权限"、"事务" |
| 发送飞书 | "飞书"、"异步"、"消息" |

### 3.2 深层 Key

抽象类型，对应思维框架：

| 抽象类型 | 思维框架 |
|---------|---------|
| 复杂后端逻辑 | 考虑边界条件、考虑并发、考虑数据一致性、考虑可扩展性 |
| 系统设计 | CAP 定理、Trade-off 分析、分而治之 |
| 抽象理论讨论 | 定义问题边界、逻辑推导、反例检验 |
| 简单 CRUD | 快速实现、基本验证、避免过度设计 |

### 3.3 Key 提取

```python
class KeyExtractor:
    """提取表层 + 深层 Key"""

    ABSTRACTION_TYPES = [
        "简单 CRUD",
        "复杂后端逻辑",
        "系统设计",
        "抽象理论讨论",
        "数据分析",
        "前端复杂交互",
    ]

    def extract(self, task: Task) -> tuple[list[str], str]:
        """提取表层 Key 和深层抽象"""

        # 用 LLM 提取
        prompt = f"""
        分析这个任务：

        {task.description}

        1. 提取表层 Key（具体标签，用逗号分隔）：
        2. 判断深层抽象类型（从以下选择：{', '.join(self.ABSTRACTION_TYPES)}）：

        输出格式：
        表层: key1, key2, key3
        深层: xxx
        """

        result = llm.call(prompt)
        # 解析结果...
        return surface_keys, abstraction
```

---

## 4. 自然语言注入

### 4.1 设计原则

不用 XML 标签，用自然的"我之前"语句，让 agent 感受到是经验而非数据。

### 4.2 实现

```python
def format_surface_memory(memory: MemoryNode) -> str:
    """表层记忆：用'之前我做'的方式"""
    return f"之前我做 {memory.scenario} 的时候，{memory.core}"


def format_deep_memory(abstraction: str, memories: list[MemoryNode]) -> str:
    """深层记忆：用'处理这类问题'的方式"""
    frameworks = "\n".join(f"- {m.core}" for m in memories)
    return f"""
处理「{abstraction}」这类问题时，我的思考方式通常是：
{frameworks}
"""


def build_context_prompt(
    surface_memories: list[MemoryNode],
    abstraction: str,
    deep_memories: list[MemoryNode]
) -> str:
    """组装完整上下文"""

    parts = []

    # 表层经验
    if surface_memories:
        lines = ["我之前做过类似的事情："]
        lines.extend(f"- {format_surface_memory(m)}" for m in surface_memories)
        parts.append("\n".join(lines))

    # 深层思维
    if deep_memories:
        parts.append(format_deep_memory(abstraction, deep_memories))

    return "\n\n".join(parts)
```

### 4.3 示例输出

```
我之前做过类似的事情：
- 之前我做 修改用户权限 的时候，权限修改前先检查数据一致性，避免脏数据
- 之前我做 权限操作 的时候，需要记录审计日志
- 之前我做 飞书消息处理 的时候，采用异步方式避免阻塞

处理「复杂后端逻辑」这类问题时，我的思考方式通常是：
- 考虑边界条件
- 考虑并发
- 考虑数据一致性
- 考虑可扩展性
```

---

## 5. Skills 加载

> 不在本文讨论，使用 DeerFlow 成熟方案

DeerFlow SKILL.md 格式是标准，运行时用 Key 索引筛选应该加载的 Skills。

---

## 6. 晶体/流体分层

### 6.1 晶体记忆

| 来源 | 说明 | 加载 |
|-----|------|-----|
| system_prompt | 系统指令 | 始终 |
| SOUL.md | agent identity | 始终 |
| USER.md | 用户偏好 | 始终 |
| core_skills | 核心技能 | 始终 |

### 6.2 流体记忆

- Key-Memory 结构，动态加载
- scenario + core 格式，自然语言注入
- 任务执行后写入

---

## 7. 待讨论问题

- [ ] Key 关系图：预定义还是自动学习？
- [ ] 存储选型：先用简单结构验证
- [ ] 深层抽象类型：需要哪些？

---

## 8. 参考

- DeerFlow prompt 注入方式
- MCP 协议