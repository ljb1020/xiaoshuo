import sys
import re
import os
import argparse
from difflib import unified_diff


def load_rules():
    """加载规则。审核规避为硬替换，去AI味为扫描报警。"""
    # 审核规避：硬性替换（平台和谐底线，必须自动修正）
    censorship_rules = {
        r"(?<!龙)中国(?!.*龙国)": "龙国",
        r"(?<![樱花])日本": "樱花国",
        r"(?<![鹰])美国": "鹰酱",
        r"(?<![鹰酱])美军": "鹰酱军",
        r"苏联": "毛熊",
        r"俄罗斯": "毛熊",
        r"(?<![约翰牛])英国": "约翰牛",
        r"(?<![高卢鸡])法国": "高卢鸡",
        r"(?<![汉斯猫])德国": "汉斯猫",
        r"055(?:大驱|级|舰|驱逐舰)": "0VV大驱",
        r"(?:歼20|歼-20|J-?20)": "J-VV隐身战机",
        r"075(?:两栖舰|级|舰)": "0QV两栖舰",
        r"99A(?:主战坦克|坦克|式)": "9VA坦克",
    }

    # 去AI味：仅扫描报警，不自动替换（由 agent 二次改句）
    ai_warning_patterns = {
        r"总而言之": "机械过渡词，建议改写",
        r"综上所述": "机械过渡词，建议改写",
        r"不仅如此": "机械过渡词，建议改写",
        r"然而不可思议的是": "典型AI句式，建议简化",
        r"倒吸一?口凉气": "机械反应词，建议用具体动作替代",
        r"嘴角勾起一抹(?:冷笑|弧度)": "机械表情词，建议用具体动作替代",
        r"深邃的眼眸": "机械外貌词，建议用具体描写替代",
        r"宛如一幅画卷": "过度修辞，建议删除或改写",
    }

    return censorship_rules, ai_warning_patterns


def lint_replace(content, rules_dict):
    """对内容执行硬性替换，返回 (新内容, 替换记录列表)。"""
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

    modified = re.sub(r'  +', ' ', modified)
    modified = re.sub(r'^ +', '', modified, flags=re.MULTILINE)

    return modified, changes


def lint_warn(content, patterns_dict):
    """扫描内容中的AI味特征词，仅报警不替换。返回警告列表。"""
    warnings = []

    for pattern, suggestion in patterns_dict.items():
        matches = list(re.finditer(pattern, content))
        for m in matches:
            line_num = content[:m.start()].count('\n') + 1
            line_content = content.splitlines()[line_num - 1] if line_num <= len(content.splitlines()) else ""
            warnings.append({
                'line': line_num,
                'matched': m.group(),
                'suggestion': suggestion,
                'context': line_content.strip()[:80],
            })

    return warnings


def show_diff(original, modified, filepath):
    """显示 unified diff 输出。"""
    orig_lines = original.splitlines(keepends=True)
    mod_lines = modified.splitlines(keepends=True)
    diff = unified_diff(orig_lines, mod_lines,
                        fromfile=f"a/{os.path.basename(filepath)}",
                        tofile=f"b/{os.path.basename(filepath)}")
    return ''.join(diff)


def main():
    parser = argparse.ArgumentParser(description='铁血纪元审核 Linter — 硬替换 + 软报警')
    parser.add_argument('filepath', help='要检查的 markdown 文件路径')
    parser.add_argument('--dry-run', action='store_true',
                        help='仅输出 diff，不修改文件')
    parser.add_argument('--verbose', action='store_true',
                        help='输出每次替换的行号和上下文')
    parser.add_argument('--censorship-only', action='store_true',
                        help='只执行审核规避替换，跳过去AI味扫描')
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

    censorship_rules, ai_warning_patterns = load_rules()

    # === 第一层：审核规避硬替换 ===
    modified, censor_changes = lint_replace(content, censorship_rules)

    # === 第二层：去AI味软报警（不替换） ===
    ai_warnings = []
    if not args.censorship_only:
        ai_warnings = lint_warn(modified, ai_warning_patterns)

    # 输出结果
    has_issues = bool(censor_changes) or bool(ai_warnings)

    if not has_issues:
        print(f"✅ Linter 通过: {os.path.basename(filepath)} 无违禁词。")
        return

    # 硬替换结果
    if censor_changes:
        if args.verbose:
            print(f"\n🔴 审核规避替换 ({len(censor_changes)} 处):")
            print("-" * 60)
            for c in sorted(censor_changes, key=lambda x: x['line']):
                print(f"  L{c['line']:>4d}: 「{c['original']}」→「{c['replacement']}」")
            print("-" * 60)

        diff_text = show_diff(content, modified, filepath)
        if diff_text:
            print(f"\n📝 Diff:\n{diff_text}")

        if args.dry_run:
            print(f"\n⚠️  Dry-run: {len(censor_changes)} 处审核规避词待替换，文件未修改。")
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified)
            print(f"\n✅ 审核规避: 自动替换了 {len(censor_changes)} 处违禁词。")

    # 软报警结果（不修改文件）
    if ai_warnings:
        print(f"\n⚠️  去AI味扫描 ({len(ai_warnings)} 处警告，不自动修改):")
        print("-" * 60)
        for w in sorted(ai_warnings, key=lambda x: x['line']):
            print(f"  L{w['line']:>4d}: 「{w['matched']}」— {w['suggestion']}")
            print(f"         上下文: {w['context']}")
        print("-" * 60)
        print("💡 以上为建议项，请 agent 根据上下文二次改句，不要机械替换。")

    if not censor_changes and ai_warnings:
        print(f"\n✅ 审核规避: 通过（无违禁词）。")


if __name__ == "__main__":
    main()
