import os
import sys

# Regex to match the standard timeline table row
# We don't strictly regex, just split by section headers and parsing tables

def parse_timeline(content):
    """
    Parse a timeline markdown file into frontmatter and three data pools:
    Canonical, Resolved, Recent.
    Returns: frontmatter, canonical_rows, resolved_rows, recent_rows
    """
    frontmatter = ""
    rest = content
    if content.startswith("---\n"):
        end_idx = content.find("\n---\n", 4)
        if end_idx != -1:
            frontmatter = content[:end_idx + 5]
            rest = content[end_idx + 5:]

    canonical = []
    resolved = []
    recent = []
    
    current_pool = recent # default to recent if no headers found
    
    for line in rest.splitlines():
        if "核心设定与重大节点" in line or "Canonical" in line:
            current_pool = canonical
            continue
        if "已闭环" in line or "Resolved" in line:
            current_pool = resolved
            continue
        if "近期上下文" in line or "Recent" in line:
            current_pool = recent
            continue
            
        stripped = line.strip()
        if stripped.startswith("|") and not stripped.startswith("| When") and not stripped.startswith("|---"):
            # Old 4-column format check vs new 5-column format
            parts = [p.strip() for p in stripped.split('|') if p.strip()]
            if len(parts) == 4:
                # 兼容升级：如果只有 4 列 (When, Event, Arc, Chapter)，强制插入 Type 列 (默认为 action)
                stripped = f"| {parts[0]} | {parts[1]} | action | {parts[2]} | {parts[3]} |"
            current_pool.append(stripped)
            
    return frontmatter, canonical, resolved, recent

def compress_timeline(timeline_path, threshold=20):
    if not os.path.exists(timeline_path):
        print(f"Error: {timeline_path} does not exist.")
        return

    with open(timeline_path, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter, canonical, resolved, recent = parse_timeline(content)

    # 第一步：基于词表的语义分发 (Semantic Routing)
    new_recent = []
    for r in recent:
        parts = [p.strip() for p in r.split('|') if p.strip()]
        if len(parts) >= 5:
            r_type = parts[2].lower()
            if r_type in ['fact', 'major_change']:
                canonical.append(r)
                changed = True
                continue
            elif r_type == 'resolved':
                resolved.append(r)
                changed = True
                continue
        # 不是晋升或已闭环的，继续留在 new_recent
        new_recent.append(r)
        
    recent = new_recent

    # 第二步：基于剩余 Recent 的过期淘汰 (Action Eviction)
    if len(recent) > threshold:
        # 只允许淘汰 action
        # 保护 rules: foreshadow, conflict 绝对不动
        evictable_candidates = []
        for i, r in enumerate(recent):
            parts = [p.strip() for p in r.split('|') if p.strip()]
            if len(parts) >= 5:
                r_type = parts[2].lower()
                if r_type == 'action':
                    evictable_candidates.append(i)
        
        excess = len(recent) - threshold
        if excess > 0 and evictable_candidates:
            # 优先从最老的（头部）action开始淘汰，最多淘汰 excess 条
            to_evict = evictable_candidates[:excess]
            for idx in reversed(to_evict):
                resolved.append(recent[idx]) # 将老旧 action 归入已闭环归档区
                del recent[idx]
            changed = True

    # Force format upgrade even if no compression occurred, if the sections are missing
    if "## 📌 核心设定与重大节点" not in content or "Type" not in content:
        changed = True

    if changed:
        with open(timeline_path, 'w', encoding='utf-8') as f:
            if frontmatter:
                f.write(frontmatter)
            f.write("\n# Timeline Memory (分层记忆池)\n")
            f.write("\n> 该文件由脚本自动维护。Agent 追加时请放在底部的 `近期上下文` 表格中。\n> 允许的 Type 必须从以下 6 个枚举中选择：`fact, action, foreshadow, conflict, resolved, major_change`。\n\n")
            
            f.write("## 📌 核心设定与重大节点 (Canonical)\n")
            f.write("| When | Event | Type | Arc | Chapter |\n")
            f.write("|------|-------|------|-----|---------|\n")
            for r in canonical:
                f.write(f"{r}\n")
            f.write("\n")
                
            f.write("## 🗄️ 已闭环 / 已归档事件 (Resolved & Archived)\n")
            f.write("| When | Event | Type | Arc | Chapter |\n")
            f.write("|------|-------|------|-----|---------|\n")
            for r in resolved:
                f.write(f"{r}\n")
            f.write("\n")
                
            f.write("## 🕒 近期上下文 (Recent)\n")
            f.write("| When | Event | Type | Arc | Chapter |\n")
            f.write("|------|-------|------|-----|---------|\n")
            for r in recent:
                f.write(f"{r}\n")
                
        print(f"Timeline Check: Upgraded/Compressed structure. Recent pool now has {len(recent)} items.")
    else:
        print(f"Timeline Check: Currently {len(recent)} recent events. No compression needed (<{threshold}).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compress_timeline.py <path_to_timeline.md>")
        sys.exit(1)
    compress_timeline(sys.argv[1])
