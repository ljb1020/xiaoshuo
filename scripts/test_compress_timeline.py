import pytest
import os
import tempfile
from compress_timeline import compress_timeline

def test_compress_timeline_upgrade_format():
    """测试将旧版单一表格升级为三层结构的逻辑"""
    old_content = """---
type: timeline
story: test
---

# Story Timeline

| When | Event | Arc | Chapter |
|------|-------|-----|---------|
| 1 | event1 | a1 | 1 |
| 2 | event2 | a1 | 2 |
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(old_content)
        path = f.name
        
    try:
        compress_timeline(path)
        with open(path, 'r', encoding='utf-8') as f:
            new_content = f.read()
            
        # 验证是否生成了三个分层
        assert "## 📌 核心设定与重大节点 (Canonical)" in new_content
        assert "## 🗄️ 已闭环事件 (Resolved)" in new_content
        assert "## 🕒 近期上下文 (Recent)" in new_content
        
        # 验证旧事件进入了 Recent
        assert "| 1 | event1 | a1 | 1 |" in new_content
        assert "| 2 | event2 | a1 | 2 |" in new_content
    finally:
        os.unlink(path)

def test_compress_timeline_exceeds_threshold():
    """测试 Recent 超过阈值后自动移入 Resolved"""
    content = """---
type: timeline
---
## 📌 核心设定与重大节点 (Canonical)
| When | Event | Arc | Chapter |
|------|-------|-----|---------|
| 0 | 设定1 | a0 | 0 |

## 🗄️ 已闭环事件 (Resolved)
| When | Event | Arc | Chapter |
|------|-------|-----|---------|
| 1 | 旧事件 | a1 | 1 |

## 🕒 近期上下文 (Recent)
| When | Event | Arc | Chapter |
|------|-------|-----|---------|
"""
    # 凑满 22 条 Recent (假设脚本把阈值设为 20)
    for i in range(2, 24):
        content += f"| {i} | recent{i} | a1 | {i} |\n"
        
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(content)
        path = f.name
        
    try:
        compress_timeline(path, threshold=20)
        with open(path, 'r', encoding='utf-8') as f:
            new_content = f.read()
            
        # Resolved 应该包含了 1（原有的）以及 2, 3（超出的两条）
        resolved_section = new_content.split("## 🕒 近期上下文 (Recent)")[0].split("## 🗄️ 已闭环事件 (Resolved)")[1]
        assert "| 1 | 旧事件" in resolved_section
        assert "| 2 | recent2" in resolved_section
        assert "| 3 | recent3" in resolved_section
        
        # Recent 应该只剩 20 条 (4 到 23)
        recent_section = new_content.split("## 🕒 近期上下文 (Recent)")[1]
        assert "| 3 | recent3" not in recent_section
        assert "| 4 | recent4" in recent_section
        assert "| 23 | recent23" in recent_section
    finally:
        os.unlink(path)
