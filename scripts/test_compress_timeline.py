import pytest
import os
import tempfile
from compress_timeline import compress_timeline

def test_compress_timeline_upgrade_format():
    """测试将旧版单一表格升级为三层结构，并自动补全 Type 列"""
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
        
        # 验证旧事件进入了 Recent，且自动被赋予了 action 类型
        assert "| 1 | event1 | action | a1 | 1 |" in new_content
        assert "| 2 | event2 | action | a1 | 2 |" in new_content
    finally:
        os.unlink(path)

def test_compress_timeline_semantic_routing():
    """测试 4 个核心场景：晋升、闭环、保护、过期淘汰"""
    content = """---
type: timeline
---
## 📌 核心设定与重大节点 (Canonical)
| When | Event | Type | Arc | Chapter |
|------|-------|------|-----|---------|
| 0 | 设定1 | fact | a0 | 0 |

## 🗄️ 已闭环事件 (Resolved)
| When | Event | Type | Arc | Chapter |
|------|-------|------|-----|---------|

## 🕒 近期上下文 (Recent)
| When | Event | Type | Arc | Chapter |
|------|-------|------|-----|---------|
| 1 | 新设定 | fact | a1 | 1 |
| 2 | 重大变化 | major_change | a1 | 2 |
| 3 | 已解决 | resolved | a1 | 3 |
| 4 | 免死伏笔 | foreshadow | a1 | 4 |
| 5 | 免死冲突 | conflict | a1 | 5 |
| 6 | 动作A | action | a1 | 6 |
"""
    # 填充大量 action 以触发阈值 (设阈值为 5，即 current_recent 数量 > 5 才淘汰)
    for i in range(7, 12):
        content += f"| {i} | 动作{i} | action | a1 | {i} |\n"
        
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(content)
        path = f.name
        
    try:
        compress_timeline(path, threshold=5)
        with open(path, 'r', encoding='utf-8') as f:
            new_content = f.read()
            
        canonical_section = new_content.split("## 🗄️ 已闭环事件")[0]
        resolved_section = new_content.split("## 🕒 近期上下文")[0].split("## 🗄️ 已闭环事件")[1]
        recent_section = new_content.split("## 🕒 近期上下文")[1]
        
        # 1. 晋升测试：fact 和 major_change 被提拔到了 Canonical
        assert "| 1 | 新设定 | fact" in canonical_section
        assert "| 2 | 重大变化 | major_change" in canonical_section
        
        # 2. 闭环测试：resolved 自己去了 Resolved
        assert "| 3 | 已解决 | resolved" in resolved_section
        
        # 3. 保护测试：foreshadow 和 conflict 仍留在 Recent，即使超量
        assert "| 4 | 免死伏笔 | foreshadow" in recent_section
        assert "| 5 | 免死冲突 | conflict" in recent_section
        
        # 4. 淘汰测试：原本 Recent 总量有很多，超过 threshold=5。
        # recent_initial_state = [foreshadow, conflict, 动作A, 动作7, 动作8, 动作9, 动作10, 动作11] (共8条)
        # excess = 8 - 5 = 3。所以最老的 3 个 action (动作A, 动作7, 动作8) 应该被淘汰进 resolved。
        assert "| 6 | 动作A | action" in resolved_section
        assert "| 7 | 动作7 | action" in resolved_section
        assert "| 8 | 动作8 | action" in resolved_section
        
        # 剩下的 action 和 被保护的 应该还在 Recent
        assert "| 9 | 动作9 | action" in recent_section
        assert "| 11 | 动作11 | action" in recent_section

    finally:
        os.unlink(path)
