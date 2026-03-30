# 项目路径与命名约定 (Conventions)

> **[Agent 必读]**：本文件定义了所有 skill 和 workflow 在执行时必须遵守的路径规则。违反本约定将导致文件丢失或上下文污染。

---

## 1. Story Project Root（故事实例根目录）

每个小说项目是一个独立的文件夹，位于 workspace 根目录下。命名使用 kebab-case。

```
xiaoshuo/                     ← workspace 根目录
├── .agents/                  ← 通用插件层（skill + workflow），不属于任何单一项目
├── 写作指南.md               ← 人类操作手册
├── 启动提示词.txt             ← AI 系统提示词
└── tiexue-jiyuan/            ← ★ 具体小说项目根目录（Story Project Root）
    ├── story.md
    ├── characters/
    ├── worldbuilding/
    ├── plot/
    ├── chapters/
    └── scripts/
```

**定位规则**：
- Skill 和 Workflow 内部引用的路径（如 `characters/`、`plot/timeline.md`）**全部相对于 Story Project Root**
- 当前活跃项目通过 `chapters/_index.md` 的 `story` frontmatter 字段识别
- 如果 workspace 下存在多个项目文件夹，Agent 必须先确认当前操作的是哪个项目

## 2. Workflow 路径前缀

`auto-writer.md` 等 workflow 中引用的路径使用 **Story Project Root 相对路径**：
- ✅ `chapters/_index.md`
- ✅ `plot/master-outline.md`
- ✅ `scripts/linter.py`
- ❌ ~~`tiexue-jiyuan/chapters/_index.md`~~（不要在 workflow 里硬编码项目名）

`启动提示词.txt` 因为位于 workspace 根目录，路径带项目名前缀：
- ✅ `tiexue-jiyuan/story.md`

## 3. 文件命名规则

| 类型 | 规则 | 示例 |
|------|------|------|
| 角色文件 | kebab-case 姓名拼音 | `chen-yuan.md`, `hasegawa-yuo.md` |
| 地点文件 | kebab-case 英文描述 | `shanghai-1937.md`, `taiwan-base.md` |
| 系统文件 | kebab-case 英文描述 | `dragon-fleet.md`, `world-factions.md` |
| Arc 文件 | `arc-{卷号}-{英文关键词}.md` | `arc-1-arrival.md`, `arc-5-blockade.md` |
| 章节文件 | `chapter-{NN}.md`（两位数补零） | `chapter-01.md`, `chapter-99.md` |
| 索引文件 | 统一使用 `_index.md` | 每个领域目录一个 |

## 4. YAML Frontmatter 约定

所有 entity 文件**必须**有 YAML frontmatter。最小必备字段：

| 文件类型 | 必备字段 |
|----------|----------|
| 角色 | `name`, `role`, `status` |
| 地点 | `name`, `type`, `region`, `status` |
| 系统 | `name`, `type` |
| Arc | `name`, `type`, `status`, `characters` |
| 章节 | `title`, `number`, `volume`, `pov`, `status`, `word-count` |
| 索引 | `type`, `story` |

## 5. 跨引用规则

- **双向链接**：当 A 引用 B 时，B 也必须引用 A
- **角色标识符**：使用 kebab-case 文件名（无 `.md` 后缀），如 `chen-yuan`
- **章节引用**：使用 `第N章` 或 `chapter-{NN}` 格式

## 6. Shell 与命令执行约定

- **Shell 环境**：Windows PowerShell。**禁止使用 `&&` 连接命令**，必须使用 `;` 分隔。
  - ✅ `git add -A; git commit -m "msg"`
  - ❌ ~~`git add -A && git commit -m "msg"`~~
- **自动执行**：用户已安装自动批准插件，所有 `run_command` 均可设置 `SafeToAutoRun: true`。

