import sys
import re
import os
import argparse
from difflib import unified_diff


def load_rules():
    """加载替换规则。分为两类：审核规避（硬性）和去AI味（建议性）。"""
    # 审核规避：硬性替换
    censorship_rules = {
        # 国家与势力（注意：华夏是合法架空代称，不替换）
        r"(?<!龙)中国(?!.*龙国)": "龙国",
        r"(?<![樱花])日本": "樱花国",
        r"(?<![鹰])美国": "鹰酱",
        r"(?<![鹰酱])美军": "鹰酱军",
        r"苏联": "毛熊",
        r"俄罗斯": "毛熊",
        r"(?<![约翰牛])英国": "约翰牛",
        r"(?<![高卢鸡])法国": "高卢鸡",
        r"(?<![汉斯猫])德国": "汉斯猫",

        # 敏感武器型号
        r"055(?:大驱|级|舰|驱逐舰)": "0VV大驱",
        r"(?:歼20|歼-20|J-?20)": "J-VV隐身战机",
        r"075(?:两栖舰|级|舰)": "0QV两栖舰",
        r"99A(?:主战坦克|坦克|式)": "9VA坦克",
    }

    # 去AI味：替换为更自然的表达
    anti_ai_rules = {
        r"总而言之": "——",
        r"综上所述": "由此可见",
        r"不仅如此": "更关键的是",
        r"然而不可思议的是": "但",
        r"倒吸一?口凉气": "浑身一颤",
        r"嘴角勾起一抹(?:冷笑|弧度)": "眼神骤然冰冷",
        r"深邃的眼眸": "锐利的目光",
        r"宛如一幅画卷": "",
    }

    return censorship_rules, anti_ai_rules


def lint_content(content, rules_dict):
    """对内容执行替换，返回 (新内容, 替换记录列表)。"""
    modified = content
    changes = []

    for pattern, replacement in rules_dict.items():
        matches = list(re.finditer(pattern, modified))
        if matches:
            for m in reversed(matches):
                line_num = modified[:m.start()].count('\n') + 1
                line_content = modified.splitlines()[line_num - 1] if line_num <= len(modified.splitlines()) else ""
                changes.append({
                    'line': line_num,
                    'original': m.group(),
                    'replacement': replacement,
                    'context': line_content.strip()[:80],
                })
            modified = re.sub(pattern, replacement, modified)

    # 清理空字符串替换导致的多余空格
    modified = re.sub(r'  +', ' ', modified)
    modified = re.sub(r'^ +', '', modified, flags=re.MULTILINE)

    return modified, changes


def show_diff(original, modified, filepath):
    """显示 unified diff 输出。"""
    orig_lines = original.splitlines(keepends=True)
    mod_lines = modified.splitlines(keepends=True)
    diff = unified_diff(orig_lines, mod_lines,
                        fromfile=f"a/{os.path.basename(filepath)}",
                        tofile=f"b/{os.path.basename(filepath)}")
    diff_text = ''.join(diff)
    return diff_text


def main():
    parser = argparse.ArgumentParser(description='铁血纪元审核 Linter — 关键词替换与去AI味检查')
    parser.add_argument('filepath', help='要检查的 markdown 文件路径')
    parser.add_argument('--dry-run', action='store_true',
                        help='仅输出 diff，不修改文件')
    parser.add_argument('--verbose', action='store_true',
                        help='输出每次替换的行号和上下文')
    parser.add_argument('--censorship-only', action='store_true',
                        help='只执行审核规避替换，跳过去AI味替换')
    args = parser.parse_args()

    filepath = args.filepath
    if not os.path.exists(filepath):
        print(f"❌ Error: {filepath} does not exist.")
        sys.exit(1)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        sys.exit(1)

    censorship_rules, anti_ai_rules = load_rules()

    # 执行审核规避替换
    modified, censor_changes = lint_content(content, censorship_rules)

    # 执行去AI味替换（除非指定了 --censorship-only）
    ai_changes = []
    if not args.censorship_only:
        modified, ai_changes = lint_content(modified, anti_ai_rules)

    all_changes = censor_changes + ai_changes

    if not all_changes:
        print(f"✅ Linter 通过: {os.path.basename(filepath)} 无违禁词。")
        return

    # 输出详情
    if args.verbose:
        print(f"\n📋 替换明细 ({len(all_changes)} 处):")
        print("-" * 60)
        for c in sorted(all_changes, key=lambda x: x['line']):
            print(f"  L{c['line']:>4d}: 「{c['original']}」→「{c['replacement']}」")
            print(f"         上下文: {c['context']}")
        print("-" * 60)

    # 输出 diff
    diff_text = show_diff(content, modified, filepath)
    if diff_text:
        print(f"\n📝 Diff:\n{diff_text}")

    # 写入或提示
    if args.dry_run:
        print(f"\n⚠️  Dry-run 模式: 发现 {len(all_changes)} 处需替换，文件未修改。")
        print(f"   移除 --dry-run 参数以执行实际替换。")
    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(modified)
        print(f"\n✅ Linter 完成: 替换了 {len(all_changes)} 处违禁词/AI特征词。")


if __name__ == "__main__":
    main()
