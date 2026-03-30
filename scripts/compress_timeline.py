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
        if "已闭环事件" in line or "Resolved" in line:
            current_pool = resolved
            continue
        if "近期上下文" in line or "Recent" in line:
            current_pool = recent
            continue
            
        stripped = line.strip()
        if stripped.startswith("|") and not stripped.startswith("| When") and not stripped.startswith("|---"):
            current_pool.append(stripped)
            
    return frontmatter, canonical, resolved, recent

def compress_timeline(timeline_path, threshold=20):
    if not os.path.exists(timeline_path):
        print(f"Error: {timeline_path} does not exist.")
        return

    with open(timeline_path, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter, canonical, resolved, recent = parse_timeline(content)

    if len(recent) > threshold:
        # Move excess from recent to resolved
        excess = len(recent) - threshold
        resolved.extend(recent[:excess])
        recent = recent[excess:]
        changed = True
    else:
        changed = False

    # Force format upgrade even if no compression occurred, if the sections are missing
    if "## 📌 核心设定与重大节点" not in content:
        changed = True

    if changed:
        with open(timeline_path, 'w', encoding='utf-8') as f:
            if frontmatter:
                f.write(frontmatter)
            f.write("\n# Timeline Memory (分层记忆池)\n")
            f.write("\n> 该文件由脚本自动维护。Agent 追加时请放在底部的 `近期上下文` 表格中。\n\n")
            
            f.write("## 📌 核心设定与重大节点 (Canonical)\n")
            f.write("| When | Event | Arc | Chapter |\n")
            f.write("|------|-------|-----|---------|\n")
            for r in canonical:
                f.write(f"{r}\n")
            f.write("\n")
                
            f.write("## 🗄️ 已闭环事件 (Resolved)\n")
            f.write("| When | Event | Arc | Chapter |\n")
            f.write("|------|-------|-----|---------|\n")
            for r in resolved:
                f.write(f"{r}\n")
            f.write("\n")
                
            f.write("## 🕒 近期上下文 (Recent)\n")
            f.write("| When | Event | Arc | Chapter |\n")
            f.write("|------|-------|-----|---------|\n")
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
