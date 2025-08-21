import streamlit as st
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from services.openai_servce import get_openai_service
from components.tree_display import render_tree_display


def render_outline_edit_page() -> Dict:
    """
    渲染目录编辑页面
    
    Returns:
        包含目录数据的字典
    """
    st.markdown("### 📚 第二步：编辑和优化标书目录结构")
    
    # 初始化状态
    _init_session_state()
    
    # 检查前置条件
    if not _check_prerequisites():
        return {"outline_data": None}
    
    # 渲染控制面板
    _render_control_panel()
    
    # 处理目录生成
    if st.session_state.generating_outline and not st.session_state.outline_generated:
        _handle_outline_generation()
    
    # 显示目录树
    if st.session_state.outline_data:
        _render_outline_tree()
    
    # 处理弹窗
    _handle_dialogs()
    
    return {"outline_data": st.session_state.outline_data}


def _init_session_state():
    """初始化session state变量"""
    defaults = {
        'outline_data': None,
        'outline_generated': False,
        'generating_outline': False,
        'show_add_dialog': False,
        'show_edit_dialog': False,
        'editing_chapter': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _check_prerequisites() -> bool:
    """检查前置条件是否满足"""
    if not st.session_state.get('project_overview') or not st.session_state.get('tech_requirements'):
        st.warning("⚠️ 请先完成第一步的标书解析，获取项目概述和技术评分要求。")
        return False
    return True


def _render_control_panel():
    """渲染控制面板（生成、新增按钮等）"""
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
        if st.button(
            "🔄 正在生成..." if st.session_state.generating_outline else "🚀 生成目录",
            type="primary",
            disabled=st.session_state.generating_outline,
            use_container_width=True,
            help="基于项目概述和技术要求生成标书目录结构"
        ):
            st.session_state.generating_outline = True
            st.session_state.outline_generated = False
            st.rerun()
    
    with col2:
        # 新增目录项按钮
        if st.button(
            "➕ 新增目录项",
            disabled=not st.session_state.outline_data,
            use_container_width=True,
            help="在现有目录中添加新的目录项"
        ):
            # 关闭编辑弹窗，避免冲突
            st.session_state.show_edit_dialog = False
            st.session_state.editing_chapter = None
            st.session_state.show_add_dialog = True
    
    with col3:
        # 状态显示
        _render_status_indicator()
    
    st.markdown("</div>", unsafe_allow_html=True)


def _render_status_indicator():
    """渲染状态指示器"""
    if st.session_state.outline_data:
        status_html = """
        <div style="
            background-color: #d4edda;
            color: #155724;
            padding: 10px 15px;
            border-radius: 8px;
            border-left: 4px solid #28a745;
            font-weight: 500;
        ">
            ✅ 目录已生成
        </div>
        """ if st.session_state.outline_generated else """
        <div style="
            background-color: #cce5ff;
            color: #004085;
            padding: 10px 15px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
            font-weight: 500;
        ">
            💾 目录已加载
        </div>
        """
    else:
        status_html = """
        <div style="
            background-color: #fff3cd;
            color: #856404;
            padding: 10px 15px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
            font-weight: 500;
        ">
            📝 请先生成目录
        </div>
        """
    st.markdown(status_html, unsafe_allow_html=True)


def _handle_outline_generation():
    """处理目录生成"""
    with st.spinner("🤖 正在生成目录，请稍后..."):
        outline_data = _generate_outline()
        if outline_data:
            st.session_state.outline_data = outline_data
            st.session_state.outline_generated = True
            st.session_state.generating_outline = False
            st.rerun()


def _generate_outline() -> Optional[Dict]:
    """生成目录数据"""
    try:
        openai_service = get_openai_service()
        overview = st.session_state.project_overview
        requirements = st.session_state.tech_requirements
        
        if not overview or not requirements:
            st.error("⚠️ 项目概述或技术要求为空")
            return None
        
        # 调用AI生成目录
        outline_json = ""
        for chunk in openai_service.generate_outline(overview, requirements):
            outline_json += chunk
        
        if not outline_json.strip():
            st.error("🤖 AI服务返回空内容")
            return None
        
        # 解析JSON
        outline_data = json.loads(outline_json)
        
        # 验证数据结构
        if not _validate_outline_structure(outline_data):
            return None
        
        return outline_data
        
    except json.JSONDecodeError as e:
        st.error(f"📝 解析目录数据失败：{str(e)}")
        return None
    except Exception as e:
        st.error(f"🚨 生成目录时发生错误：{str(e)}")
        return None


def _validate_outline_structure(data: Dict) -> bool:
    """验证目录数据结构"""
    if not isinstance(data, dict) or 'outline' not in data:
        st.error("📋 目录数据格式错误")
        return False
    
    if not isinstance(data['outline'], list) or len(data['outline']) == 0:
        st.error("📋 目录为空")
        return False
    
    # 递归验证每个章节
    return all(_validate_chapter(ch, 0) for ch in data['outline'])


def _validate_chapter(chapter: Dict, level: int) -> bool:
    """验证单个章节"""
    # 检查必需字段
    if not isinstance(chapter, dict):
        return False
    
    required = ['id', 'title']
    if not all(field in chapter and isinstance(chapter[field], str) and chapter[field].strip() 
               for field in required):
        return False
    
    # 检查层级限制（最多3级）
    if 'children' in chapter:
        if level >= 2:  # 已经是第3级，不能再有子级
            if chapter['children']:
                st.error(f"章节 {chapter['id']} 超过最大层级限制")
                return False
        elif isinstance(chapter['children'], list):
            return all(_validate_chapter(child, level + 1) for child in chapter['children'])
    
    return True


def _render_outline_tree():
    """渲染目录树"""
    def handle_edit(chapter_data, path):
        """处理编辑操作"""
        # 关闭其他弹窗，避免冲突
        st.session_state.show_add_dialog = False
        st.session_state.editing_chapter = {
            'path': path,
            'chapter': chapter_data
        }
        st.session_state.show_edit_dialog = True
        st.rerun()
    
    def handle_delete(path):
        """处理删除操作"""
        # 关闭所有弹窗
        st.session_state.show_add_dialog = False
        st.session_state.show_edit_dialog = False
        st.session_state.editing_chapter = None
        
        if _delete_chapter_by_path(path):
            # 删除后重排序号
            _renumber_all_chapters()
            st.success("✅ 章节已删除")
            st.rerun()
    
    # 使用树形显示组件
    render_tree_display(
        st.session_state.outline_data,
        on_edit=handle_edit,
        on_delete=handle_delete,
        key_prefix="outline_tree"
    )


def _handle_dialogs():
    """处理弹窗"""
    # 确保同时只显示一个弹窗
    if st.session_state.show_add_dialog:
        _show_add_dialog()
    elif st.session_state.show_edit_dialog:  # 使用elif避免同时打开两个弹窗
        _show_edit_dialog()


@st.dialog("➕ 新增目录项")
def _show_add_dialog():
    """显示新增目录项弹窗"""
    chapters_tree = _build_chapters_tree()
    
    if not chapters_tree:
        st.error("没有可用的目录项")
        if st.button("关闭"):
            st.session_state.show_add_dialog = False
            st.rerun()
        return
    
    # 选择操作类型
    operation = st.radio(
        "选择操作",
        ["添加同级目录", "添加子目录"],
        horizontal=True
    )
    
    # 选择目标章节
    target = st.selectbox(
        "选择目标位置",
        chapters_tree,
        format_func=lambda x: x['display']
    )
    
    # 输入新章节信息
    st.markdown("---")
    title = st.text_input("标题", placeholder="请输入标题")
    description = st.text_area("描述（可选）", placeholder="请输入描述", height=80)
    
    # 检查是否可以添加
    can_add = title.strip() and target
    if operation == "添加子目录" and target and target['level'] >= 2:
        st.warning("⚠️ 已达到最大层级限制（3级）")
        can_add = False
    
    # 操作按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 确定", disabled=not can_add, use_container_width=True, type="primary"):
            is_child = (operation == "添加子目录")
            if _add_chapter(target, title.strip(), description.strip(), is_child):
                st.session_state.show_add_dialog = False
                st.rerun()
    
    with col2:
        if st.button("❌ 取消", use_container_width=True):
            st.session_state.show_add_dialog = False
            st.rerun()


@st.dialog("✏️ 编辑目录项")
def _show_edit_dialog():
    """显示编辑目录项弹窗"""
    if not st.session_state.editing_chapter:
        st.error("未找到要编辑的章节")
        if st.button("关闭"):
            st.session_state.show_edit_dialog = False
            st.rerun()
        return
    
    chapter = st.session_state.editing_chapter['chapter']
    path = st.session_state.editing_chapter['path']
    
    # 显示当前信息
    st.info(f"章节ID: {chapter.get('id', '')}")
    
    # 编辑表单
    title = st.text_input("标题", value=chapter.get('title', ''))
    description = st.text_area("描述", value=chapter.get('description', ''), height=100)
    
    # 操作按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 保存", disabled=not title.strip(), use_container_width=True, type="primary"):
            if _update_chapter_by_path(path, title.strip(), description.strip()):
                st.session_state.editing_chapter = None
                st.session_state.show_edit_dialog = False
                st.success("✅ 章节已更新")
                st.rerun()
    
    with col2:
        if st.button("❌ 取消", use_container_width=True):
            st.session_state.editing_chapter = None
            st.session_state.show_edit_dialog = False
            st.rerun()


# ============ 辅助函数 ============

def _build_chapters_tree() -> List[Dict]:
    """构建章节树供选择"""
    if not st.session_state.outline_data:
        return []
    
    result = []
    _collect_chapters(st.session_state.outline_data['outline'], result, "", 0)
    return result


def _collect_chapters(chapters: List[Dict], result: List[Dict], parent_path: str, level: int):
    """递归收集章节"""
    for i, chapter in enumerate(chapters):
        path = f"{parent_path}.{i}" if parent_path else str(i)
        
        # 添加缩进和图标
        indent = "　" * level  # 使用全角空格
        icon = ["📁", "📂", "📄"][min(level, 2)]
        
        result.append({
            'path': path,
            'level': level,
            'chapter': chapter,
            'display': f"{indent}{icon} {chapter['id']} {chapter['title']}"
        })
        
        # 递归处理子章节
        if 'children' in chapter and chapter['children'] and level < 2:
            _collect_chapters(chapter['children'], result, path, level + 1)


def _get_chapter_by_path(path: str) -> Tuple[Optional[List], Optional[int]]:
    """根据路径获取章节的父列表和索引"""
    if not st.session_state.outline_data:
        return None, None
    
    parts = path.split('.')
    chapters = st.session_state.outline_data['outline']
    
    for i, part in enumerate(parts):
        try:
            index = int(part)
            if i == len(parts) - 1:
                # 最后一部分，返回父列表和索引
                return chapters, index
            elif 0 <= index < len(chapters):
                # 继续向下查找
                if 'children' not in chapters[index]:
                    chapters[index]['children'] = []
                chapters = chapters[index]['children']
            else:
                return None, None
        except (ValueError, IndexError):
            return None, None
    
    return None, None


def _delete_chapter_by_path(path: str) -> bool:
    """根据路径删除章节"""
    parent, index = _get_chapter_by_path(path)
    if parent is not None and index is not None and 0 <= index < len(parent):
        del parent[index]
        return True
    return False


def _update_chapter_by_path(path: str, title: str, description: str) -> bool:
    """根据路径更新章节"""
    parent, index = _get_chapter_by_path(path)
    if parent is not None and index is not None and 0 <= index < len(parent):
        parent[index]['title'] = title
        parent[index]['description'] = description
        return True
    return False


def _add_chapter(target: Dict, title: str, description: str, as_child: bool) -> bool:
    """添加新章节"""
    try:
        # 创建新章节（先用临时ID）
        new_chapter = {
            'id': 'temp',
            'title': title,
            'description': description,
            'children': []
        }
        
        if as_child:
            # 添加为子章节
            success = _add_child_by_path(target['path'], new_chapter)
        else:
            # 添加为同级章节
            parent, index = _get_chapter_by_path(target['path'])
            if parent is not None and index is not None:
                parent.insert(index + 1, new_chapter)
                success = True
            else:
                success = False
        
        if success:
            # 添加成功后重新排序所有章节
            _renumber_all_chapters()
            return True
        else:
            return False
        
    except Exception as e:
        st.error(f"添加失败：{str(e)}")
        return False


def _renumber_all_chapters():
    """重新为所有章节分配序号"""
    if not st.session_state.outline_data or 'outline' not in st.session_state.outline_data:
        return
    
    _renumber_chapters_recursive(st.session_state.outline_data['outline'], "")


def _renumber_chapters_recursive(chapters: List[Dict], parent_id: str):
    """递归重新编号章节"""
    for i, chapter in enumerate(chapters):
        # 生成新的ID
        if parent_id:
            new_id = f"{parent_id}.{i + 1}"
        else:
            new_id = str(i + 1)
        
        # 更新章节ID
        chapter['id'] = new_id
        
        # 递归处理子章节
        if 'children' in chapter and chapter['children']:
            _renumber_chapters_recursive(chapter['children'], new_id)


def _add_child_by_path(path: str, new_chapter: Dict) -> bool:
    """根据路径直接添加子章节"""
    if not st.session_state.outline_data:
        return False
    
    parts = path.split('.')
    chapters = st.session_state.outline_data['outline']
    
    # 逐级查找目标章节
    for i, part in enumerate(parts):
        try:
            index = int(part)
            if 0 <= index < len(chapters):
                if i == len(parts) - 1:
                    # 找到目标章节，添加子章节
                    if 'children' not in chapters[index]:
                        chapters[index]['children'] = []
                    chapters[index]['children'].append(new_chapter)
                    return True
                else:
                    # 继续向下查找
                    if 'children' not in chapters[index]:
                        chapters[index]['children'] = []
                    chapters = chapters[index]['children']
            else:
                return False
        except (ValueError, IndexError):
            return False
    
    return False
