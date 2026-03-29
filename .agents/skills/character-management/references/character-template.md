# Character Template

Use this template when creating a new character file at `characters/{character-name-kebab}.md`.

```yaml
---
name: "{Full Name}"
role: {protagonist|antagonist|supporting|minor}
age: {age}
status: {alive|deceased|unknown}
aliases:
  - "{Alias 1}"
relationships:
  - character: {other-character-kebab}
    type: {relationship-type}
tags:
  - {tag-1}
  - {tag-2}
arc: {character-arc-theme}
---
```

## Appearance

Physical description: build, height, distinguishing features, typical clothing, how they carry themselves.

## Personality & Traits

Core personality traits, temperament, habits, quirks. What makes them memorable in a scene.

## Backstory

Key events that shaped who they are. Only include what's relevant to the story.

## Motivations & Goals

What drives them. What they want (external goal) and what they need (internal goal). How these conflict.

## Voice & Speech Patterns (Voice Bank)

> **[CRITICAL — 防 OOC 铁律]**：此区域是长篇连载中防止角色"千人一面"的核心锚点。AI 在写任何章节对话前，**必须**先读取本区域的语料。

**说话风格**：{语速/用词/句式习惯/口头禅/方言特征}

**专属语料库（3-5 条标志性台词）**：
> "{台词1 — 最能代表角色核心气质的一句话}"
> "{台词2 — 情绪激动时的典型反应}"
> "{台词3 — 冷静/日常状态下的典型用语}"
> "{台词4 — 面对敌人/对手时的态度}"
> "{台词5 — 可选，幽默/自嘲/特殊场合}"

**绝对禁区**：{列出该角色绝不会说的话/用的词，防止 AI 串味}

## Character Arc

- **Starting state:** Where they begin emotionally/psychologically
- **Key turning points:** What changes them
- **Ending state:** Where they end up (or projected end)

## Timeline

Key life events in chronological order:

| When | Event | Relevance |
|------|-------|-----------|
| | | |

## Dynamic Status（动态状态栏）

> **[Agent 必读]**：每章写完后，若该角色有状态变化，必须更新此栏。写新章节前，必须读取此栏确认角色当前状态。

| 字段 | 当前值 |
|------|--------|
| **身体状态** | {健康/轻伤/重伤/昏迷/死亡} |
| **情绪基调** | {当前主导情绪} |
| **当前位置** | {地点} |
| **持有情报/秘密** | {列出该角色目前知道但其他人不知道的信息} |
| **最后出场章节** | 第 {N} 章 |

### 关系变化日志
| 章节 | 变化内容 |
|------|----------|
| | |

### 出场章节记录
{列出所有出场章节号，用逗号分隔}
