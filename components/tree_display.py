import streamlit as st
from typing import Dict, List, Callable, Any
import hashlib

def render_tree_display(
    outline_data: Dict,
    on_edit: Callable[[Dict, str], None] = None,
    on_delete: Callable[[str], None] = None,
    key_prefix: str = "tree"
) -> None:
    """
    渲染简约美观的树形目录结构（静态展示）

    Args:
        outline_data: 目录数据
        on_edit: 编辑回调函数 (chapter_data, path) -> None
        on_delete: 删除回调函数 (path) -> None
        key_prefix: 组件key前缀，用于区分不同实例
    """
    if not outline_data or 'outline' not in outline_data:
        st.warning("暂无目录数据")
        return

    st.markdown("### 📋 标书目录结构")
    
    # 添加自定义CSS样式
    st.markdown("""
    <style>
        .tree-item {
            display: flex;
            align-items: center;
            padding: 8px 0;
            border-left: 2px solid #e0e0e0;
            margin-left: 10px;
            position: relative;
        }
        
        .tree-item::before {
            content: "";
            position: absolute;
            left: -2px;
            top: 50%;
            width: 10px;
            height: 2px;
            background-color: #e0e0e0;
        }
        
        .tree-item.root {
            border-left: none;
            margin-left: 0;
        }
        
        .tree-item.root::before {
            display: none;
        }
        
        .tree-content {
            display: flex;
            align-items: center;
            gap: 8px;
            padding-left: 15px;
            font-size: 14px;
        }
        
        .tree-icon {
            font-size: 16px;
        }
        
        .tree-title {
            font-weight: 500;
            color: #333;
        }
        
        .tree-description {
            color: #666;
            font-size: 12px;
            margin-left: 40px;
            padding: 4px 0;
        }
    </style>
    """, unsafe_allow_html=True)

    # 渲染树形结构
    _render_tree_simple(outline_data['outline'], on_edit, on_delete, key_prefix, 0, "")

def _render_tree_simple(
    chapters: List[Dict],
    on_edit: Callable = None,
    on_delete: Callable = None,
    key_prefix: str = "tree",
    level: int = 0,
    parent_path: str = ""
) -> None:
    """渲染简约的树形结构"""
    
    for i, chapter in enumerate(chapters):
        current_path = f"{parent_path}.{i}" if parent_path else str(i)
        chapter_id = chapter.get('id', f'ch_{i}')
        title = chapter.get('title', '未命名章节')
        description = chapter.get('description', '')
        has_children = 'children' in chapter and chapter['children'] and len(chapter['children']) > 0
        
        # 渲染章节内容
        _render_chapter_simple(
            chapter_id, title, description, level, 
            current_path, key_prefix,
            on_edit, on_delete, chapter
        )
        
        # 递归渲染子章节
        if has_children:
            _render_tree_simple(
                chapter['children'], 
                on_edit, 
                on_delete, 
                key_prefix, 
                level + 1, 
                current_path
            )
def _render_chapter_simple(
    chapter_id: str,
    title: str,
    description: str,
    level: int,
    path: str,
    key_prefix: str,
    on_edit: Callable,
    on_delete: Callable,
    chapter: Dict
):
    """渲染简约的章节项"""
    
    # 根据层级设置图标和样式
    if level == 0:
        icon = "📘"  # 一级目录
        tree_line = ""
    elif level == 1:
        icon = "📑"  # 二级目录
        tree_line = "├──"
    else:
        icon = "📄"  # 三级目录
        tree_line = "│   └──"
    
    # 创建列布局
    col1, col2, col3 = st.columns([6, 1, 1])
    
    with col1:
        # 构建显示内容
        indent = "" if level == 0 else ("　" * (level * 2))
        
        # 使用容器包装整个章节
        with st.container():
            # 显示标题行
            if level == 0:
                # 一级标题加粗显示
                st.markdown(f"{icon} **{chapter_id}. {title}**")
            elif level == 1:
                # 二级标题正常显示
                st.markdown(f"{indent}{tree_line} {icon} {chapter_id} {title}")
            else:
                # 三级标题稍小显示
                st.markdown(f"{indent}{tree_line} {icon} {chapter_id} {title}")
            
            # 显示描述（如果有）
            if description:
                desc_indent = indent + ("　" * 3)
                st.caption(f"{desc_indent}{description}")
    
    with col2:
        if on_edit:
            edit_key = f"edit_{key_prefix}_{path}_{hashlib.md5(str(path + chapter_id + title).encode()).hexdigest()[:8]}"
            if st.button("✏️", key=edit_key, help="编辑", type="primary"):
                chapter_data = {
                    'id': chapter_id,
                    'title': title,
                    'description': description,
                    'children': chapter.get('children', [])
                }
                on_edit(chapter_data, path)
    
    with col3:
        if on_delete:
            delete_key = f"delete_{key_prefix}_{path}_{hashlib.md5(str(path + chapter_id + title).encode()).hexdigest()[:8]}"
            if st.button("🗑️", key=delete_key, help="删除", type="secondary"):
                on_delete(path)

