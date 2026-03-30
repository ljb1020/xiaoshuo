---
description: 自动续写最新章节流水线（单章物理隔离模式）
---
这个工作流将帮你自动找寻当前小说的最新进度，并采用严格物理隔离的"新窗逻辑"，每次只专注生成并审核单一章节的大纲与正文，最后自动更新时间线和目录。为了保证上下文不被积压污染，每执行一次本流程，就是一次完全闭环、高度锁定的正文入库过程。

> **[重要]**：本工作流的"物理隔离"依赖**每章使用一个新的对话窗口**。AI 无法在同一个对话中自动清空自己的上下文。每章完成后，用户应开启新对话并重新输入 `/auto-writer`。所有"记忆"通过文件系统（timeline.md、角色卡等）持久化，而非保存在 AI 的上下文中。

> **路径约定**：本 workflow 中所有以 `$NOVEL/` 开头的路径表示**当前小说项目根目录**（如 `tiexue-jiyuan/`）；所有以 `$ROOT/` 开头的路径表示 **workspace 根目录**（如 `xiaoshuo/`）。脚本位于 `$ROOT/scripts/`，小说文件位于 `$NOVEL/` 内部。

0. **第零步：定位小说根目录 (Locate Novel Root)**
   - 检查用户当前打开的文件或最近活跃的 workspace，识别当前小说项目根目录（`$NOVEL`）。
   - 确认方式：找到包含 `chapters/_index.md` 的目录，读取其 `story` frontmatter 字段。
   - 确认 workspace 根目录（`$ROOT`）：`$NOVEL` 的上级目录。

1. **第一步：进度嗅探与定位 (Progress Sniffing)**
   - 读取并解析 `$NOVEL/chapters/_index.md`，找到目前系统中已完成存储的最大章节号。
   - 将这章定为进度锚点 `N-1`。本次工作流的核心目标自动锁定为生成 **第 `N` 章**。
   - 打开 `$NOVEL/plot/master-outline.md`，精准抓取大纲里关于 **第 `N` 章** 的核心剧情爆点与要求。
   - 同时读取对应的卷 arc 文件（`$NOVEL/plot/arcs/arc-{卷号}-*.md`）获取更细的章节纲要。

2. **第二步：构筑无菌防崩坏环境 (Context Sandbox)**

   **必读文件（每章强制加载）：**
   - 读取 `$NOVEL/story.md` 获取全局避讳词、情感基调、台词风格、修辞限速与去AI味写作规范。
   - 读取 `$NOVEL/plot/timeline.md` 获取到 `N-1` 章节为止的小说实时时间线记忆。
   - 查询 `$NOVEL/plot/foreshadowing.md`，检查本章是否需要回收伏笔。
   - 从 `$NOVEL/characters/` 目录调取第 `N` 章对应必须出场的核心人物卡片（务必包含 Voice Bank 专属语料库、**短句杀器**和 Dynamic Status 动态状态栏）。

   **条件读取（按章节类型加载）：**
   - 战斗章 → 读取 `$NOVEL/worldbuilding/systems/dragon-fleet.md`（战力规则）+ `$NOVEL/worldbuilding/systems/ija-order-of-battle.md`（敌方兵力）
   - 种田章 → 读取 `$NOVEL/worldbuilding/systems/china-1937-economy.md`（工业/经济约束）
   - 涉及地点描写 → 读取对应 `$NOVEL/worldbuilding/locations/*.md`

   **章节分型判定**：根据 arc 大纲中本章的定位，明确本章是「爆发章」还是「蓄力章」，并提取本章的**核心冲突点**和**章末钩子方向**。

3. **第三步：对靶 + 分镜细纲 (Chapter Task Card + Outline)**

   **3a. 本章任务卡（必须先完成，不准跳过）：**
   在写任何细纲之前，先明确回答以下五项：
   1. **一句话目标**：本章在全卷推进中到底要完成什么？
   2. **最大爽点**：读者读完这章最爽/最燃/最揪心的那一刻是什么？
   3. **张力来源**：这章的紧迫感从何而来？（不限于内部争吵——可以是时限、资源、敌方动态、认知冲突等）
   4. **名场面**：本章是否有需要五感降速的名场面？如果有，是哪个段落？
   5. **结尾牵引点**：章末靠什么让读者想点下一章？（不一律是悬念——也可以是期待、余波、即将兑现的承诺）

   **⛔ 任务卡闸门**：如果一句话目标空泛（如"推进剧情"）、张力来源无法落到具体场景、或爽点与牵引点明显不成立，则**禁止进入正文**，必须重新对靶直到五项都具体可执行。

   **3b. 四拍分镜细纲：**
   基于任务卡，用四拍节奏组织正文结构（参考框架，非硬性模板）：
   - 爆发章参考：「钩子 → 加压 → 爆发 → 更大钩子」
   - 蓄力章参考：「悬念切入 → 推进 → 微型爆发 → 牵引升级」
   - 细纲中应体现任务卡中确认的爽点和名场面的位置。
   - （等待用户确认，或直接进入第四步）

4. **第四步：正文生成与审查 (Writing & Linter)**
   - 按四拍结构分段构思，一次性保存完整正文到 `$NOVEL/chapters/chapter-{NN}.md`（两位数补零）。
   - 正文目标 **2000-2500 字**。**正文中不得包含任何内部结构标记**。
   - **执行硬性代码 Linter**：强制静默执行 `python $ROOT/scripts/linter.py $NOVEL/chapters/chapter-{NN}.md`。
   - **处理 Linter 输出**：
     * 🔴 审核规避替换：Linter 会自动完成，无需额外操作。
     * ⚠️ 去AI味警告：Linter 会输出警告位置和建议。Agent 必须逐条审阅，根据上下文二次改句（不要机械替换），改完后无需重跑 Linter。
   - **反 AI 质检**：检查长短句结合是否到位？名场面段落是否使用了五感降速？本章是否至少有一处只属于这个角色/场景的表达？

4.5 **API 截断与防呆鉴权校验 (Failsafe Check)【绝对红线】**
   - 强制执行 `python $ROOT/scripts/wordcount.py $NOVEL/chapters/chapter-{NN}.md` 进行字数校验。
   - 检查正文总字数是否达到 **2000字以上**，且段落结尾是否为完整的句号/感叹号结构。
   - **如果字数不足或截断：** 立即终止！严禁执行第五步！清理残骸并报错。

5. **第五步：记忆固化落地与大修剪 (Commit Memory & Compress)**
   - 将本章核心事件追加至 `$NOVEL/plot/timeline.md`。
   - **执行记忆防膨胀压缩**：`python $ROOT/scripts/compress_timeline.py $NOVEL/plot/timeline.md`。
   - 更新 `$NOVEL/chapters/_index.md`。
   - **更新角色动态状态**：更新出场角色的 Dynamic Status。
   - **更新敌方战损**（如有战斗）：在 `$NOVEL/worldbuilding/systems/ija-order-of-battle.md` 中标注。
   - 向用户报告："✅ 第 {N} 章已完成合规入库。请开启新对话窗口，输入 /auto-writer 开始第 {N+1} 章。"
