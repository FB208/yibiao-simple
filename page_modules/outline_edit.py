import streamlit as st
import json
import uuid
from typing import Dict, List, Any, Tuple, Optional
from services.openai_servce import get_openai_service

def render_outline_edit_page() -> Dict:
    """
    渲染目录编辑页面

    Returns:
        包含目录数据的字典
    """

    st.markdown("### 📚第二步：编辑和优化标书目录结构")
    
    # 初始化弹窗状态
    if 'show_add_dialog' not in st.session_state:
        st.session_state.show_add_dialog = False

    # 初始化 session_state 变量
    if 'outline_data' not in st.session_state:
        st.session_state.outline_data = None
    if 'outline_generated' not in st.session_state:
        st.session_state.outline_generated = False
    if 'generating_outline' not in st.session_state:
        st.session_state.generating_outline = False
    if 'editing_chapter' not in st.session_state:
        st.session_state.editing_chapter = None
    if 'show_add_form' not in st.session_state:
        st.session_state.show_add_form = False

    # 检查是否有必要的数据
    if not st.session_state.get('project_overview') or not st.session_state.get('tech_requirements'):
        st.warning("⚠️ 请先完成第一步的标书解析，获取项目概述和技术评分要求。")
        return {"outline_data": None}

    # 操作按钮区域
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    ">
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.2, 1.2, 1.6])
    
    with col1:
        # 生成目录按钮
        generate_disabled = st.session_state.generating_outline
        generate_label = "🔄 正在生成..." if generate_disabled else "🚀 生成目录"
        
        if st.button(
            generate_label, 
            type="primary", 
            disabled=generate_disabled,
            use_container_width=True,
            help="基于项目概述和技术要求生成标书目录结构"
        ):
            st.session_state.generating_outline = True
            st.session_state.outline_generated = False
            st.rerun()
    
    with col2:
        # 新增目录项按钮
        add_disabled = not st.session_state.outline_data
        if st.button(
            "➕ 新增目录项", 
            disabled=add_disabled,
            use_container_width=True,
            help="在现有目录中添加新的目录项"
        ):
            st.session_state.show_add_dialog = True
    
    with col3:
        # 状态显示区域
        if st.session_state.outline_data:
            if st.session_state.outline_generated:
                st.markdown("""
                <div style="
                    background-color: #d4edda;
                    color: #155724;
                    padding: 10px 15px;
                    border-radius: 8px;
                    border-left: 4px solid #28a745;
                    font-weight: 500;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                ">
                    ✅ 目录已生成并保存
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background-color: #cce5ff;
                    color: #004085;
                    padding: 10px 15px;
                    border-radius: 8px;
                    border-left: 4px solid #007bff;
                    font-weight: 500;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                ">
                    💾 目录将自动保存
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background-color: #fff3cd;
                color: #856404;
                padding: 10px 15px;
                border-radius: 8px;
                border-left: 4px solid #ffc107;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                📝 请先生成目录
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # 如果正在生成，显示 loading 状态
    if st.session_state.generating_outline and not st.session_state.outline_generated:
        _display_loading_state()

        # 执行目录生成
        outline_data = _generate_outline_data()
        if outline_data:
            st.session_state.outline_data = outline_data
            st.session_state.outline_generated = True
            st.session_state.generating_outline = False
            st.rerun()

    # 显示和编辑目录
    if st.session_state.outline_generated and st.session_state.outline_data:
        _render_editable_outline()

    # 新增目录项弹窗
    if st.session_state.show_add_dialog:
        _show_add_dialog()

    return {"outline_data": st.session_state.outline_data}

def _display_loading_state():
    """显示加载状态"""
    st.markdown("---")
    with st.spinner(""):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="
                text-align: center;
                padding: 40px;
                border: 2px solid #e1e4e8;
                border-radius: 10px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-size: 18px;
                font-weight: bold;
            ">
                🤖 正在生成目录，请稍后...
            </div>
            """, unsafe_allow_html=True)



def _generate_outline_data() -> Dict[str, Any]:
    """
    生成目录数据

    Returns:
        目录数据字典
    """
    try:
        # 获取 OpenAI 服务
        openai_service = get_openai_service()

        # 获取项目概述和技术要求
        overview = st.session_state.project_overview
        requirements = st.session_state.tech_requirements

        if not overview or not requirements:
            st.error("⚠️ 项目概述或技术要求为空，无法生成目录")
            return None

        # 生成目录
        outline_json = ""
        try:
            for chunk in openai_service.generate_outline(overview, requirements):
                outline_json += chunk
        except Exception as api_error:
            st.error(f"🤖 AI 服务调用失败：{str(api_error)}")
            st.error("请检查网络连接或稍后重试")
            return None

        if not outline_json.strip():
            st.error("🤖 AI 服务返回空内容，请重试")
            return None

        # 解析 JSON
        try:
            outline_data = json.loads(outline_json)
        except json.JSONDecodeError as json_error:
            st.error(f"📝 解析目录数据失败：{str(json_error)}")
            st.error("AI 返回的数据格式不正确，请重新生成")
            with st.expander("🔍 查看原始数据", expanded=False):
                st.text(outline_json)
            return None

        # 验证目录数据结构
        if not _validate_outline_data(outline_data):
            st.error("📋 目录数据结构验证失败，请重新生成")
            return None

        return outline_data

    except Exception as e:
        st.error(f"🚨 生成目录时发生未知错误：{str(e)}")
        st.error("请刷新页面后重试，或联系技术支持")
        return None

def _render_editable_outline():
    """渲染可编辑的目录树"""
    st.markdown("---")
    st.markdown("### 📋 标书目录结构")

    outline_data = st.session_state.outline_data

    if not outline_data or 'outline' not in outline_data:
        st.error("目录数据格式错误")
        return

    # 渲染目录树
    _render_editable_tree_level(outline_data['outline'], 0)

def _render_editable_tree_level(chapters: List[Dict], level: int = 0, parent_path: str = ""):
    """
    递归渲染可编辑的目录层级

    Args:
        chapters: 章节列表
        level: 当前层级
        parent_path: 父级路径
    """
    for i, chapter in enumerate(chapters):
        current_path = f"{parent_path}.{i}" if parent_path else str(i)
        _render_editable_chapter(chapter, level, current_path, chapters, i)

        if 'children' in chapter and chapter['children']:
            _render_editable_tree_level(chapter['children'], level + 1, current_path)

def _render_editable_chapter(chapter: Dict, level: int, path: str, parent_chapters: List[Dict], index: int):
    """
    渲染可编辑的单个章节

    Args:
        chapter: 章节数据
        level: 层级
        path: 章节路径
        parent_chapters: 父级章节列表
        index: 在父级中的索引
    """
    title = chapter.get('title', '未命名章节')
    description = chapter.get('description', '')
    chapter_id = chapter.get('id', '')

    # 根据层级设置图标和样式
    if level == 0:
        icon = "📁"
        header_level = "###"
    elif level == 1:
        icon = "📂"
        header_level = "####"
    else:
        icon = "📄"
        header_level = "#####"

    # 使用expander来展示章节内容
    with st.expander(f"{icon} {chapter_id} {title}", expanded=(level == 0)):
        # 章节信息
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            if description:
                st.caption(description)

        with col2:
            if st.button("✏️ 编辑", key=f"edit_{path}", use_container_width=True):
                st.session_state.editing_chapter = {
                    'path': path,
                    'chapter': chapter,
                    'parent_chapters': parent_chapters,
                    'index': index
                }

        with col3:
            if st.button("🗑️ 删除", key=f"delete_{path}", use_container_width=True):
                _delete_chapter(parent_chapters, index)
                st.success("章节已删除")
                st.rerun()

    # 编辑表单
    if (st.session_state.editing_chapter and
        st.session_state.editing_chapter['path'] == path):
        _render_edit_form()

def _render_edit_form():
    """渲染编辑表单"""
    edit_data = st.session_state.editing_chapter
    chapter = edit_data['chapter']

    st.markdown("---")
    st.markdown("#### ✏️ 编辑章节")

    with st.form(key=f"edit_form_{edit_data['path']}"):
        new_title = st.text_input("章节标题", value=chapter.get('title', ''))
        new_description = st.text_area("章节描述", value=chapter.get('description', ''), height=80)

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 保存修改", use_container_width=True):
                _update_chapter(edit_data, new_title, new_description)
                st.session_state.editing_chapter = None
                st.success("章节已更新")
                st.rerun()

        with col2:
            if st.form_submit_button("❌ 取消", use_container_width=True):
                st.session_state.editing_chapter = None
                st.rerun()

def _render_add_chapter_form():
    """渲染新增目录表单"""
    st.markdown("---")
    st.markdown("#### ➕ 新增目录项")
    
    # 获取目录结构用于选择
    chapter_tree = _build_chapter_tree()
    
    with st.form(key="add_chapter_form"):
        # 简化的操作选择
        col1, col2 = st.columns(2)
        with col1:
            operation = st.radio(
                "📍 选择操作",
                options=["添加同级章节", "添加子章节"],
                index=0,
                help="选择要执行的操作类型"
            )
        
        with col2:
            # 显示操作说明
            if operation == "添加同级章节":
                st.info("🔄 将在选中章节的后面添加一个同级章节")
            else:
                st.info("📁 将在选中章节的下面添加一个子章节")
        
        # 选择目标章节
        if chapter_tree:
            target_chapter = st.selectbox(
                "🎯 选择目标章节",
                options=chapter_tree,
                format_func=lambda x: x['display_name'],
                help="选择要在哪个章节附近添加新章节"
            )
        else:
            st.warning("没有找到可用的章节")
            target_chapter = None
            
        # 新章节信息输入
        st.markdown("##### 📝 新章节信息")
        new_title = st.text_input("章节标题", placeholder="请输入章节标题")
        new_description = st.text_area(
            "章节描述", 
            placeholder="请输入章节描述（可选）",
            height=80
        )
        
        # 预览新章节位置
        if target_chapter and new_title.strip():
            _render_add_chapter_preview(operation, target_chapter, new_title.strip())
        
        # 操作按钮
        col1, col2 = st.columns(2)
        with col1:
            submit_disabled = not (target_chapter and new_title.strip())
            if st.form_submit_button(
                "✅ 添加章节", 
                use_container_width=True,
                disabled=submit_disabled
            ):
                if new_title.strip():
                    success, message = _add_chapter_by_tree_selection(
                        operation,
                        target_chapter,
                        new_title.strip(),
                        new_description.strip()
                    )
                    if success:
                        st.session_state.show_add_form = False
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("章节标题不能为空")

        with col2:
            if st.form_submit_button("❌ 取消", use_container_width=True):
                st.session_state.show_add_form = False
                st.rerun()

def _get_chapter_options():
    """获取可用的父级章节选项"""
    options = ["根目录"]
    if st.session_state.outline_data and 'outline' in st.session_state.outline_data:
        _collect_chapter_options(st.session_state.outline_data['outline'], options, "", 1)
    return options

def _get_chapter_options_for_insert():
    """获取可用于插入位置的章节选项"""
    options = []
    if st.session_state.outline_data and 'outline' in st.session_state.outline_data:
        _collect_chapter_options_for_insert(st.session_state.outline_data['outline'], options, "", 1)
    return options

def _collect_chapter_options(chapters: List[Dict], options: List[str], prefix: str, level: int):
    """递归收集章节选项"""
    for i, chapter in enumerate(chapters):
        option = f"{prefix}{chapter.get('id', str(i+1))} {chapter.get('title', '未命名')}"
        options.append(option)

        if 'children' in chapter and chapter['children'] and level < 3:
            _collect_chapter_options(chapter['children'], options, f"{option} > ", level + 1)

def _collect_chapter_options_for_insert(chapters: List[Dict], options: List[str], prefix: str, level: int):
    """递归收集可用于插入的章节选项"""
    for i, chapter in enumerate(chapters):
        option = f"{prefix}{chapter.get('id', str(i+1))} {chapter.get('title', '未命名')}"
        options.append(option)

        if 'children' in chapter and chapter['children']:
            _collect_chapter_options_for_insert(chapter['children'], options, f"{option} > ", level + 1)

def _update_chapter(edit_data: Dict, new_title: str, new_description: str):
    """更新章节内容"""
    chapter = edit_data['chapter']
    chapter['title'] = new_title
    chapter['description'] = new_description

def _delete_chapter(parent_chapters: List[Dict], index: int):
    """删除章节"""
    if 0 <= index < len(parent_chapters):
        del parent_chapters[index]

def _add_directory_item(insert_type: str, target_chapter: str, title: str, description: str) -> tuple[bool, str]:
    """
    添加目录项

    Args:
        insert_type: 插入方式 ("在后面插入同级目录" 或 "在下面插入子级目录")
        target_chapter: 目标章节路径
        title: 目录标题
        description: 目录描述

    Returns:
        (是否成功, 消息)
    """
    try:
        # 生成新的ID
        new_id = str(uuid.uuid4())[:8]

        # 创建新目录项
        new_item = {
            'id': new_id,
            'title': title,
            'description': description,
            'children': []
        }

        if insert_type == "在下面插入子级目录":
            # 检查是否会超过三级限制
            current_level = _get_chapter_level(target_chapter)
            if current_level >= 3:
                return False, "无法添加：已达到最大目录层级（3级）"

            # 插入为子目录
            success = _insert_as_child(st.session_state.outline_data['outline'], target_chapter, new_item)
            if success:
                return True, "子目录已添加"
            else:
                return False, "添加失败：未找到目标章节"

        else:  # "在后面插入同级目录"
            # 插入为同级目录
            success = _insert_as_sibling(st.session_state.outline_data['outline'], target_chapter, new_item)
            if success:
                return True, "同级目录已添加"
            else:
                return False, "添加失败：未找到目标章节"

    except Exception as e:
        return False, f"添加失败：{str(e)}"

def _get_chapter_level(chapter_path: str) -> int:
    """获取章节的级别"""
    if not chapter_path:
        return 0
    return chapter_path.count(" > ") + 1

def _insert_as_child(chapters: List[Dict], target_path: str, new_item: Dict) -> bool:
    """插入为子目录"""
    if not target_path:
        return False

    path_parts = target_path.split(" > ")
    return _find_and_insert_child(chapters, path_parts, new_item)

def _find_and_insert_child(chapters: List[Dict], path_parts: List[str], new_item: Dict) -> bool:
    """递归查找并插入子目录"""
    if not path_parts:
        return False

    target = path_parts[0]
    remaining_path = path_parts[1:]

    for chapter in chapters:
        chapter_title = f"{chapter.get('id', '')} {chapter.get('title', '')}".strip()
        if chapter_title == target:
            if not remaining_path:
                # 找到目标章节，插入为子目录
                if 'children' not in chapter:
                    chapter['children'] = []
                chapter['children'].append(new_item)
                return True
            else:
                # 继续向下查找
                if 'children' in chapter:
                    return _find_and_insert_child(chapter['children'], remaining_path, new_item)
    return False

def _insert_as_sibling(chapters: List[Dict], target_path: str, new_item: Dict) -> bool:
    """插入为同级目录"""
    if not target_path:
        return False

    path_parts = target_path.split(" > ")
    if len(path_parts) <= 1:
        # 在根目录下插入
        chapters.append(new_item)
        return True
    else:
        # 在父级目录中插入
        parent_path = path_parts[:-1]
        target_name = path_parts[-1]
        return _find_and_insert_sibling(chapters, parent_path, target_name, new_item)

def _find_and_insert_sibling(chapters: List[Dict], parent_path: List[str], target_name: str, new_item: Dict) -> bool:
    """递归查找并插入同级目录"""
    if not parent_path:
        # 在当前层级查找目标并在其后插入
        for i, chapter in enumerate(chapters):
            chapter_title = f"{chapter.get('id', '')} {chapter.get('title', '')}".strip()
            if chapter_title == target_name:
                chapters.insert(i + 1, new_item)
                return True
        return False

    current = parent_path[0]
    remaining_path = parent_path[1:]

    for chapter in chapters:
        chapter_title = f"{chapter.get('id', '')} {chapter.get('title', '')}".strip()
        if chapter_title == current:
            if 'children' in chapter:
                return _find_and_insert_sibling(chapter['children'], remaining_path, target_name, new_item)
    return False

# ========== 新增章节功能的辅助函数 ==========

def _build_chapter_tree() -> List[Dict]:
    """
    构建章节树结构用于选择
    
    Returns:
        章节树列表，每个元素包含 display_name, path, level 等信息
    """
    if not st.session_state.outline_data or 'outline' not in st.session_state.outline_data:
        return []
    
    tree = []
    _collect_chapter_tree_items(
        st.session_state.outline_data['outline'], 
        tree, 
        "", 
        0
    )
    return tree

def _collect_chapter_tree_items(
    chapters: List[Dict], 
    tree: List[Dict], 
    parent_path: str, 
    level: int
) -> None:
    """
    递归收集章节树项目
    
    Args:
        chapters: 章节列表
        tree: 输出树结构
        parent_path: 父级路径
        level: 当前层级
    """
    for i, chapter in enumerate(chapters):
        chapter_id = chapter.get('id', f'ch_{i}')
        chapter_title = chapter.get('title', '未命名')
        
        # 构建显示名称
        indent = "  " * level  # 使用空格缩进
        level_icon = _get_level_icon(level)
        display_name = f"{indent}{level_icon} {chapter_id} {chapter_title}"
        
        # 构建路径
        current_path = f"{parent_path}.{i}" if parent_path else str(i)
        
        tree_item = {
            'display_name': display_name,
            'path': current_path,
            'level': level,
            'chapter_id': chapter_id,
            'chapter_title': chapter_title,
            'chapter_data': chapter
        }
        tree.append(tree_item)
        
        # 递归处理子章节
        if 'children' in chapter and chapter['children'] and level < 2:  # 限制最大层级
            _collect_chapter_tree_items(
                chapter['children'], 
                tree, 
                current_path, 
                level + 1
            )

def _get_level_icon(level: int) -> str:
    """获取层级图标"""
    icons = ["📁", "📂", "📄"]
    return icons[min(level, len(icons) - 1)]

@st.dialog("⭐ 新增目录项")
def _show_add_dialog():
    """
    显示新增目录项弹窗（使用st.dialog装饰器）
    """
    _render_add_dialog()

def _render_add_dialog():
    """
    渲染新增目录项弹窗内容
    """
    # 初始化弹窗状态变量
    if 'dialog_operation' not in st.session_state:
        st.session_state.dialog_operation = "添加同级目录项"
    if 'dialog_target' not in st.session_state:
        st.session_state.dialog_target = None
    if 'dialog_title' not in st.session_state:
        st.session_state.dialog_title = ""
    if 'dialog_description' not in st.session_state:
        st.session_state.dialog_description = ""
    
    # 获取目录结构
    chapter_tree = _build_chapter_tree()
    if not chapter_tree:
        st.error("没有找到可用的目录项")
        if st.button("关闭", key="close_no_chapters"):
            st.session_state.show_add_dialog = False
            st.rerun()
        return
    
    # 操作选择
    col1, col2 = st.columns(2)
    with col1:
        new_operation = st.radio(
            "📍 选择操作",
            options=["添加同级目录项", "添加子目录项"],
            index=0 if st.session_state.dialog_operation == "添加同级目录项" else 1,
            key="dialog_operation_radio"
        )
        # 更新操作状态
        if new_operation != st.session_state.dialog_operation:
            st.session_state.dialog_operation = new_operation
            st.rerun()
    
    with col2:
        # 显示操作说明
        if st.session_state.dialog_operation == "添加同级目录项":
            st.info("🔄 将在选中目录项的后面添加一个同级目录项")
        else:
            st.info("📁 将在选中目录项的下面添加一个子目录项")
    
    # 目标目录选择
    target_chapter = st.selectbox(
        "🎯 选择目标目录项",
        options=chapter_tree,
        format_func=lambda x: x['display_name'],
        index=0 if not st.session_state.dialog_target else 
              next((i for i, item in enumerate(chapter_tree) 
                   if item['path'] == st.session_state.dialog_target['path']), 0),
        key="dialog_target_select"
    )
    st.session_state.dialog_target = target_chapter
    
    # 新目录项信息
    st.markdown("##### 📝 新目录项信息")
    
    new_title = st.text_input(
        "目录项标题", 
        value=st.session_state.dialog_title,
        placeholder="请输入目录项标题",
        key="dialog_title_input"
    )
    st.session_state.dialog_title = new_title
    
    new_description = st.text_area(
        "目录项描述",
        value=st.session_state.dialog_description,
        placeholder="请输入目录项描述（可选）",
        height=100,
        key="dialog_description_input"
    )
    st.session_state.dialog_description = new_description
    
    # 预览
    if target_chapter and new_title.strip():
        st.markdown("---")
        st.markdown("##### 🔍 预览位置")
        
        target_level = target_chapter['level']
        target_display = target_chapter['display_name'].strip()
        
        if st.session_state.dialog_operation == "添加同级目录项":
            new_level = target_level
            new_icon = _get_level_icon(new_level)
            new_indent = "  " * new_level
            preview_text = f"**在以下目录项的后面添加同级目录项：**\n\n{target_display}\n{new_indent}{new_icon} [NEW] {new_title}  ← 新目录项将在这里"
        else:
            if target_level >= 2:
                st.warning("⚠️ 无法添加：已达到最大目录层级（3级）")
            else:
                new_level = target_level + 1
                new_icon = _get_level_icon(new_level)
                new_indent = "  " * new_level
                preview_text = f"**在以下目录项的下面添加子目录项：**\n\n{target_display}\n{new_indent}{new_icon} [NEW] {new_title}  ← 新目录项将在这里"
        
        if 'preview_text' in locals():
            st.markdown(preview_text)
    
    # 操作按钮
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        can_add = (
            target_chapter and 
            new_title.strip() and 
            (st.session_state.dialog_operation == "添加同级目录项" or target_chapter['level'] < 2)
        )
        
        if st.button("✅ 添加目录项", disabled=not can_add, use_container_width=True, key="dialog_add_btn"):
            # 正确映射操作类型
            if st.session_state.dialog_operation == "添加子目录项":
                mapped_operation = "添加子章节"
            else:
                mapped_operation = "添加同级章节"
            
            success, message = _add_chapter_by_tree_selection(
                mapped_operation,
                target_chapter,
                new_title.strip(),
                new_description.strip()
            )
            
            if success:
                # 清空状态
                st.session_state.dialog_operation = "添加同级目录项"
                st.session_state.dialog_target = None
                st.session_state.dialog_title = ""
                st.session_state.dialog_description = ""
                st.session_state.show_add_dialog = False
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    with col2:
        if st.button("❌ 取消", use_container_width=True, key="dialog_cancel_btn"):
            # 清空状态
            st.session_state.dialog_operation = "添加同级目录项"
            st.session_state.dialog_target = None
            st.session_state.dialog_title = ""
            st.session_state.dialog_description = ""
            st.session_state.show_add_dialog = False
            st.rerun()

def _render_add_chapter_preview(
    operation: str, 
    target_chapter: Dict, 
    new_title: str
) -> None:
    """
    渲染新章节预览
    
    Args:
        operation: 操作类型
        target_chapter: 目标章节
        new_title: 新章节标题
    """
    st.markdown("---")
    st.markdown("##### 🔍 预览新章节位置")
    
    target_level = target_chapter['level']
    target_display = target_chapter['display_name'].strip()
    
    if operation == "添加同级章节":
        new_level = target_level
        new_icon = _get_level_icon(new_level)
        new_indent = "  " * new_level
        
        preview_text = f"""
**在以下章节的后面添加同级章节：**

{target_display}
{new_indent}{new_icon} [NEW] {new_title}  ← 新章节将在这里
        """
    else:  # 添加子章节
        if target_level >= 2:
            st.warning("⚠️ 无法添加：已达到最大目录层级（3级）")
            return
            
        new_level = target_level + 1
        new_icon = _get_level_icon(new_level)
        new_indent = "  " * new_level
        
        preview_text = f"""
**在以下章节的下面添加子章节：**

{target_display}
{new_indent}{new_icon} [NEW] {new_title}  ← 新章节将在这里
        """
    
    st.markdown(preview_text)

def _add_chapter_by_tree_selection(
    operation: str,
    target_chapter: Dict,
    title: str,
    description: str
) -> Tuple[bool, str]:
    """
    根据树结构选择添加章节
    
    Args:
        operation: 操作类型
        target_chapter: 目标章节数据
        title: 新章节标题
        description: 新章节描述
        
    Returns:
        (是否成功, 消息)
    """
    try:
        # 生成新的ID（自动编号）
        new_id = _generate_chapter_id(title, target_chapter, operation)
        
        # 创建新章节
        new_chapter = {
            'id': new_id,
            'title': title,
            'description': description,
            'children': []
        }
        
        target_path = target_chapter['path']
        target_level = target_chapter['level']
        
        if operation == "添加子章节":
            # 检查层级限制
            if target_level >= 2:
                return False, "无法添加：已达到最大目录层级（3级）"
            
            # 添加为子章节
            success = _insert_chapter_as_child(target_path, new_chapter)
            if success:
                return True, f"子章节 '{new_id} {title}' 已成功添加"
            else:
                return False, "添加失败：未找到目标章节"
        else:
            # 添加为同级章节
            success = _insert_chapter_as_sibling(target_path, new_chapter)
            if success:
                return True, f"同级章节 '{new_id} {title}' 已成功添加"
            else:
                return False, "添加失败：未找到目标章节"
                
    except Exception as e:
        return False, f"添加失败：{str(e)}"

def _generate_chapter_id(title: str, target_chapter: Dict = None, operation: str = "添加同级章节") -> str:
    """
    生成章节ID（自动编号）
    
    Args:
        title: 章节标题
        target_chapter: 目标章节数据
        operation: 操作类型
        
    Returns:
        章节ID
    """
    if not target_chapter:
        # 如果没有目标章节，生成根级编号
        return _generate_root_level_id()
    
    target_level = target_chapter['level']
    target_id = target_chapter['chapter_id']
    
    if operation == "添加子章节":
        # 生成子级编号
        return _generate_child_level_id(target_chapter)
    else:
        # 生成同级编号
        return _generate_sibling_level_id(target_chapter)

def _generate_root_level_id() -> str:
    """
    生成根级章节编号
    
    Returns:
        根级章节ID（如：1, 2, 3...）
    """
    if not st.session_state.outline_data or 'outline' not in st.session_state.outline_data:
        return "1"
    
    outline = st.session_state.outline_data['outline']
    if not outline:
        return "1"
    
    # 找到最大的根级编号
    max_num = 0
    for chapter in outline:
        chapter_id = chapter.get('id', '')
        try:
            num = int(chapter_id)
            max_num = max(max_num, num)
        except ValueError:
            # 如果不是数字，跳过
            continue
    
    return str(max_num + 1)

def _generate_child_level_id(target_chapter: Dict) -> str:
    """
    生成子级章节编号
    
    Args:
        target_chapter: 目标章节数据
        
    Returns:
        子级章节ID
    """
    target_id = target_chapter['chapter_id']
    target_data = target_chapter['chapter_data']
    
    # 获取目标章节的子章节
    children = target_data.get('children', [])
    
    if not children:
        # 第一个子章节
        return f"{target_id}.1"
    
    # 找到最大的子级编号
    max_num = 0
    prefix = f"{target_id}."
    
    for child in children:
        child_id = child.get('id', '')
        if child_id.startswith(prefix):
            try:
                # 提取子级编号
                suffix = child_id[len(prefix):]
                if '.' not in suffix:  # 确保是直接子级
                    num = int(suffix)
                    max_num = max(max_num, num)
            except ValueError:
                continue
    
    return f"{target_id}.{max_num + 1}"

def _generate_sibling_level_id(target_chapter: Dict) -> str:
    """
    生成同级章节编号
    
    Args:
        target_chapter: 目标章节数据
        
    Returns:
        同级章节ID
    """
    target_id = target_chapter['chapter_id']
    target_level = target_chapter['level']
    
    if target_level == 0:
        # 根级同级编号
        return _generate_root_level_id()
    
    # 获取父级ID和当前级别的编号部分
    id_parts = target_id.split('.')
    if len(id_parts) < 2:
        return _generate_root_level_id()
    
    parent_id = '.'.join(id_parts[:-1])
    
    # 查找同级的最大编号
    siblings = _get_siblings_at_level(target_chapter)
    max_num = 0
    prefix = f"{parent_id}."
    
    for sibling in siblings:
        sibling_id = sibling.get('id', '')
        if sibling_id.startswith(prefix):
            try:
                # 提取同级编号
                suffix = sibling_id[len(prefix):]
                if '.' not in suffix:  # 确保是直接同级
                    num = int(suffix)
                    max_num = max(max_num, num)
            except ValueError:
                continue
    
    return f"{parent_id}.{max_num + 1}"

def _get_siblings_at_level(target_chapter: Dict) -> List[Dict]:
    """
    获取目标章节的同级章节列表
    
    Args:
        target_chapter: 目标章节数据
        
    Returns:
        同级章节列表
    """
    target_path = target_chapter['path']
    path_parts = target_path.split('.')
    
    if len(path_parts) == 1:
        # 根级章节
        return st.session_state.outline_data['outline']
    
    # 找到父级章节
    parent_path = '.'.join(path_parts[:-1])
    parent_chapter = _find_chapter_by_path(parent_path)
    
    if parent_chapter and 'children' in parent_chapter:
        return parent_chapter['children']
    
    return []

def _find_chapter_by_path(path: str) -> Dict:
    """
    根据路径查找章节
    
    Args:
        path: 章节路径
        
    Returns:
        章节数据
    """
    if not st.session_state.outline_data or 'outline' not in st.session_state.outline_data:
        return None
    
    path_parts = path.split('.')
    current_chapters = st.session_state.outline_data['outline']
    
    for part in path_parts:
        try:
            index = int(part)
            if 0 <= index < len(current_chapters):
                current_chapter = current_chapters[index]
                current_chapters = current_chapter.get('children', [])
            else:
                return None
        except (ValueError, IndexError):
            return None
    
    # 返回最后一级的章节
    path_parts = path.split('.')
    current_chapters = st.session_state.outline_data['outline']
    
    for i, part in enumerate(path_parts):
        try:
            index = int(part)
            if 0 <= index < len(current_chapters):
                if i == len(path_parts) - 1:
                    return current_chapters[index]
                current_chapters = current_chapters[index].get('children', [])
            else:
                return None
        except (ValueError, IndexError):
            return None
    
    return None

def _chapter_id_exists(chapter_id: str) -> bool:
    """
    检查章节ID是否已存在
    
    Args:
        chapter_id: 要检查的章节ID
        
    Returns:
        是否存在
    """
    if not st.session_state.outline_data or 'outline' not in st.session_state.outline_data:
        return False
    
    return _search_chapter_id(st.session_state.outline_data['outline'], chapter_id)

def _search_chapter_id(chapters: List[Dict], chapter_id: str) -> bool:
    """
    递归搜索章节ID
    
    Args:
        chapters: 章节列表
        chapter_id: 要搜索的章节ID
        
    Returns:
        是否找到
    """
    for chapter in chapters:
        if chapter.get('id') == chapter_id:
            return True
        if 'children' in chapter and chapter['children']:
            if _search_chapter_id(chapter['children'], chapter_id):
                return True
    return False


# ========== 数据验证函数 ==========

def _validate_outline_data(outline_data: Dict) -> bool:
    """
    验证目录数据结构的完整性
    
    Args:
        outline_data: 目录数据
        
    Returns:
        是否验证通过
    """
    try:
        if not isinstance(outline_data, dict):
            st.error("📋 目录数据必须是字典格式")
            return False
            
        if 'outline' not in outline_data:
            st.error("📋 目录数据缺少 'outline' 字段")
            return False
            
        if not isinstance(outline_data['outline'], list):
            st.error("📋 outline 字段必须是列表格式")
            return False
            
        if len(outline_data['outline']) == 0:
            st.warning("📋 目录为空，请重新生成")
            return False
            
        # 验证每个章节
        for i, chapter in enumerate(outline_data['outline']):
            if not _validate_chapter(chapter, f"根级章节[{i}]", 0):
                return False
                
        return True
        
    except Exception as e:
        st.error(f"📋 验证目录数据时出错：{str(e)}")
        return False

def _validate_chapter(chapter: Dict, path: str, level: int) -> bool:
    """
    验证单个章节数据结构
    
    Args:
        chapter: 章节数据
        path: 章节路径（用于错误提示）
        level: 章节层级
        
    Returns:
        是否验证通过
    """
    try:
        if not isinstance(chapter, dict):
            st.error(f"📋 {path} 必须是字典格式")
            return False
            
        # 检查必需字段
        required_fields = ['id', 'title']
        for field in required_fields:
            if field not in chapter:
                st.error(f"📋 {path} 缺少必需字段: {field}")
                return False
            if not isinstance(chapter[field], str):
                st.error(f"📋 {path} 的 {field} 字段必须是字符串")
                return False
            if not chapter[field].strip():
                st.error(f"📋 {path} 的 {field} 字段不能为空")
                return False
                
        # 检查可选字段
        if 'description' in chapter and not isinstance(chapter['description'], str):
            st.error(f"📋 {path} 的 description 字段必须是字符串")
            return False
            
        # 检查子章节
        if 'children' in chapter:
            if not isinstance(chapter['children'], list):
                st.error(f"📋 {path} 的 children 字段必须是列表")
                return False
                
            # 检查层级限制
            if level >= 2 and len(chapter['children']) > 0:
                st.error(f"📋 {path} 超过最大层级限制（3级）")
                return False
                
            # 递归验证子章节
            for i, child in enumerate(chapter['children']):
                child_path = f"{path} > 子章节[{i}]"
                if not _validate_chapter(child, child_path, level + 1):
                    return False
                    
        return True
        
    except Exception as e:
        st.error(f"📋 验证章节 {path} 时出错：{str(e)}")
        return False
        
# ========== 实用工具函数 ==========

def _get_chapter_count(outline_data: Dict) -> int:
    """
    获取总章节数量
    
    Args:
        outline_data: 目录数据
        
    Returns:
        章节总数
    """
    if not outline_data or 'outline' not in outline_data:
        return 0
        
    return _count_chapters_recursive(outline_data['outline'])

def _count_chapters_recursive(chapters: List[Dict]) -> int:
    """
    递归计算章节数量
    
    Args:
        chapters: 章节列表
        
    Returns:
        章节数量
    """
    count = len(chapters)
    for chapter in chapters:
        if 'children' in chapter and chapter['children']:
            count += _count_chapters_recursive(chapter['children'])
    return count
    
def _insert_chapter_as_child(target_path: str, new_chapter: Dict) -> bool:
    """
    将章节作为子章节插入
    
    Args:
        target_path: 目标路径
        new_chapter: 新章节数据
        
    Returns:
        是否成功
    """
    return _insert_by_path(
        st.session_state.outline_data['outline'], 
        target_path.split('.'), 
        new_chapter, 
        'child'
    )

def _insert_chapter_as_sibling(target_path: str, new_chapter: Dict) -> bool:
    """
    将章节作为同级章节插入
    
    Args:
        target_path: 目标路径
        new_chapter: 新章节数据
        
    Returns:
        是否成功
    """
    return _insert_by_path(
        st.session_state.outline_data['outline'], 
        target_path.split('.'), 
        new_chapter, 
        'sibling'
    )

def _insert_by_path(
    chapters: List[Dict], 
    path_parts: List[str], 
    new_chapter: Dict, 
    insert_type: str
) -> bool:
    """
    根据路径插入章节
    
    Args:
        chapters: 章节列表
        path_parts: 路径部分
        new_chapter: 新章节
        insert_type: 插入类型 ('child' 或 'sibling')
        
    Returns:
        是否成功
    """
    if not path_parts:
        return False
    
    try:
        current_index = int(path_parts[0])
    except (ValueError, IndexError):
        return False
    
    if current_index < 0 or current_index >= len(chapters):
        return False
    
    if len(path_parts) == 1:
        # 到达目标位置
        if insert_type == 'child':
            # 作为子章节添加
            if 'children' not in chapters[current_index]:
                chapters[current_index]['children'] = []
            chapters[current_index]['children'].append(new_chapter)
        else:
            # 作为同级章节添加
            chapters.insert(current_index + 1, new_chapter)
        return True
    else:
        # 继续向下搜索
        if 'children' in chapters[current_index]:
            return _insert_by_path(
                chapters[current_index]['children'], 
                path_parts[1:], 
                new_chapter, 
                insert_type
            )
    
    return False
