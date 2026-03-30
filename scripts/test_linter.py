import sys
import os
import tempfile

# 确保能导入 linter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from linter import split_frontmatter, lint_replace, lint_warn, mask_ignored_blocks, restore_ignored_blocks

passed = 0
failed = 0


def assert_eq(name, actual, expected):
    global passed, failed
    if actual == expected:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name}")
        print(f"     期望: {expected!r}")
        print(f"     实际: {actual!r}")


# ========== 1. Frontmatter 分离 ==========
print("\n🧪 Test: split_frontmatter")

fm, body = split_frontmatter("---\ntitle: test\nstatus: draft\n---\n正文内容在这里。")
assert_eq("正确分离 frontmatter", fm, "---\ntitle: test\nstatus: draft\n---\n")
assert_eq("正确分离 body", body, "正文内容在这里。")

fm, body = split_frontmatter("没有 frontmatter 的纯正文。")
assert_eq("无 frontmatter 时返回空 fm", fm, "")
assert_eq("无 frontmatter 时返回完整 body", body, "没有 frontmatter 的纯正文。")

fm, body = split_frontmatter("---\nbroken yaml without closing")
assert_eq("未闭合 frontmatter 视为无 fm", fm, "")

# ========== 2. 审核规避替换 ==========
print("\n🧪 Test: 审核规避替换")
mock_censorship_rules = {
    "(?<!龙)中国(?!.*龙国)": "龙国",
    "(?<![樱花])日本": "樱花国",
    "055(?:大驱|级|舰|驱逐舰)": "0VV大驱"
}

# 正常替换
modified, changes = lint_replace("日本军队进攻中国领土。", mock_censorship_rules)
assert_eq("日本→樱花国", "樱花国" in modified, True)
assert_eq("中国→龙国", "龙国" in modified, True)
assert_eq("产生替换记录", len(changes) > 0, True)

# 不误伤已替换词
modified, changes = lint_replace("龙国海军在樱花国海域巡航。", mock_censorship_rules)
assert_eq("龙国不被二次处理", modified.count("龙国") == 1, True)
assert_eq("樱花国不被二次处理", modified.count("樱花国") == 1, True)
assert_eq("无替换记录", len(changes), 0)

# 武器避讳替换
modified, _ = lint_replace("055大驱发射导弹。", mock_censorship_rules)
assert_eq("055大驱→0VV大驱", "0VV大驱" in modified, True)

# ========== 3. Frontmatter 不被替换 ==========
print("\n🧪 Test: Frontmatter 保护")
fm_content = "---\ntitle: 中国的崛起\nstatus: draft\n---\n日本军队进入中国。"
fm, body = split_frontmatter(fm_content)
modified_body, changes = lint_replace(body, mock_censorship_rules)
result = fm + modified_body
assert_eq("frontmatter 中的'中国'未被替换", "title: 中国的崛起" in result, True)
assert_eq("正文中的'中国'被替换", "龙国" in result.split("---")[-1], True)
assert_eq("正文中的'日本'被替换", "樱花国" in result.split("---")[-1], True)

# ========== 4. AI 味扫描 ==========
print("\n🧪 Test: AI 味扫描")
mock_ai_patterns = {
    "总而言之": "机械过渡词",
    "倒吸一口凉气": "机械反应词"
}

warnings = lint_warn("总而言之，这场战斗非常激烈。他倒吸一口凉气。", mock_ai_patterns)
assert_eq("检出 AI 味词汇", len(warnings), 2)

warnings = lint_warn("炮弹呼啸而过，甲板上的钢板被撕裂成碎片。", mock_ai_patterns)
assert_eq("正常文本无警告", len(warnings), 0)

# ========== 5. 代码块与引用块屏蔽 ==========
print("\n🧪 Test: 区块屏蔽")
mock_ignore_config = {"skip_code_fence": True, "skip_blockquote": True}

test_body = (
    "这里的中国需要替换。\n"
    "```python\n"
    "print(\"日本和中国\")\n"
    "```\n"
    "> 日本军队也不要替换\n"
    "> 中国也是\n"
    "正文的日本需要替换。"
)

masked, masks = mask_ignored_blocks(test_body, mock_ignore_config)
assert_eq("产生代码块掩码", len([k for k in masks if 'CODE' in k]), 1)
assert_eq("产生引用块掩码", len([k for k in masks if 'QUOTE' in k]), 1)

modified_masked, _ = lint_replace(masked, mock_censorship_rules)
final_result = restore_ignored_blocks(modified_masked, masks)

assert_eq("首行正文中国被替换", final_result.startswith("这里的龙国需要替换。"), True)
assert_eq("代码块内不变", 'print("日本和中国")' in final_result, True)
assert_eq("引用块内不变", '> 日本军队也不要替换\n> 中国也是' in final_result, True)
assert_eq("末行正文日本被替换", final_result.endswith("正文的樱花国需要替换。"), True)

# ========== 结果汇总 ==========
print(f"\n{'='*40}")
print(f"  总计: {passed + failed} | ✅ {passed} | ❌ {failed}")
print(f"{'='*40}")
sys.exit(1 if failed > 0 else 0)
