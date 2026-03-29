# Chapter Template

Use this template when creating a new chapter file at `chapters/chapter-{NN}.md`.

```yaml
---
title: "{章节标题}"
number: {N}
volume: {卷号}
pov: {角色kebab-id}
locations:
  - {地点kebab-id}
characters:
  - {角色kebab-id}
arcs-advanced:
  - {卷arc-kebab}
status: draft  # outline | draft | revised | final
word-count: 0
timeline-date: "1937-XX-XX"
foreshadowing-planted: []
foreshadowing-paid: []
---
```

## 三段式分镜细纲（起·承转·合）

> **[Agent 必读]**：正文生成前必须先输出本细纲并等待确认。细纲直接决定 Chunking 质量。

### 起（Chunk 1 · ~800字）
- **开场锚点**：本段从哪个视觉/感官画面切入？
- **场景目标**：本段要完成什么交代？
- **张力来源**：冲突或悬念在哪里？
- **收束方式**：留给 Chunk 2 的接口是什么？

### 承/转（Chunk 2 · ~800字）
- **承接锚点**：如何自然跟上 Chunk 1？
- **场景目标**：推进什么核心矛盾？
- **转折/伏笔**：本段是否埋下/回收伏笔？
- **收束方式**：如何为高潮蓄力？

### 合/高潮（Chunk 3 · ~800字）
- **爆发点**：本章最强烈的戏剧冲突是什么？
- **五感降速描写区**：高潮段落列出需要慢镜头展开的感官细节
- **敌方/路人视角**：是否有 ≥30% 篇幅切换到反派或旁观者视角？
- **钩子结尾**：最后一句要达成什么悬念效果？

### 参考检查清单
- [ ] 长短句交替使用，无连续排比
- [ ] 无黑名单词汇（见 writing-guidelines.md）
- [ ] 高潮使用五感替代法，无抽象情绪形容词
- [ ] 避讳词已全部替换（中国→龙国等）
- [ ] 关键武器使用后在 dragon-fleet.md 中标记消耗

---

## 正文

{正文内容，场景之间用 `---` 分隔}
