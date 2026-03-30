# 项目路径与命名约定 (Conventions)

> **[Agent 必读]**：本文件定义了所有 skill 和 workflow 在执行时必须遵守的路径规则。违反本约定将导致文件丢失或上下文污染。

---

## 1. 两层架构

```
xiaoshuo/                     ← $ROOT — workspace 根目录（写作平台）
├── .agents/                  ← 通用插件层（skill + workflow）
├── scripts/                  ← 平台级脚本（linter、wordcount、compress_timeline）
├── 写作指南.md               ← 人类操作手册
├── GEMINI.md                 ← Agent 行为约束
├── BACKLOG.md                ← 跨窗口持久化待办清单
├── 建议.md                   ← 改进建议（可选）
└── tiexue-jiyuan/            ← $NOVEL — 小说项目根目录
    ├── story.md              ← 故事圣经（基调、规则、避讳词、去AI味规范）
    ├── characters/
    ├── worldbuilding/
    ├── plot/
    └── chapters/
```

- **$ROOT**（`xiaoshuo/`）：写作平台层。所有小说共享的工具、workflow、脚本、约定。
- **$NOVEL**（如 `tiexue-jiyuan/`）：单本小说层。story.md、角色、大纲、正文等只属于这本小说。
- 后续新增小说项目时，在 `$ROOT` 下新建平行目录（如 `novel-2/`），结构同 `tiexue-jiyuan/`。

## 2. Workflow 路径规范

`auto-writer.md` 使用 `$ROOT` 和 `$NOVEL` 变量引用路径：
- 小说文件：`$NOVEL/story.md`、`$NOVEL/chapters/_index.md`
- 平台脚本：`$ROOT/scripts/linter.py`、`$ROOT/scripts/wordcount.py`
- 不在 workflow 里硬编码项目名

**定位规则**：
- Agent 通过查找包含 `chapters/_index.md` 的目录来定位 `$NOVEL`
- `$ROOT` = `$NOVEL` 的上级目录
- 如果 workspace 下存在多个项目，Agent 必须先确认当前操作的是哪个

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
- **自动执行**：用户已安装自动批准插件，所有 `run_command` 均可设置 `SafeToAutoRun: true`。
