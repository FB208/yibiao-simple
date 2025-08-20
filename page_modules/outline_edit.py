import streamlit as st
from typing import Dict, List

def render_outline_edit_page() -> Dict:
    """
    渲染目录编辑页面
    
    Returns:
        包含目录数据的字典
    """
    
    st.header("📚 目录编辑")
    st.markdown("### 第二步：编辑和优化标书目录结构")
    
    # 目录编辑区域
    st.markdown("#### 🎯 当前目录结构")
    
    # 示例目录结构
    sample_outline = [
        "1. 项目概述",
        "   1.1 项目背景",
        "   1.2 项目目标",
        "   1.3 项目范围",
        "2. 技术方案",
        "   2.1 总体架构",
        "   2.2 技术路线",
        "   2.3 关键技术",
        "3. 实施方案",
        "   3.1 实施计划",
        "   3.2 人员配置",
        "   3.3 进度安排",
        "4. 质量保障",
        "   4.1 质量标准",
        "   4.2 控制措施",
        "   4.3 验收标准",
        "5. 服务支持",
        "   5.1 售后服务",
        "   5.2 技术支持",
        "   5.3 培训计划"
    ]
    
    # 目录编辑表格
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**目录内容**")
        # 使用文本区域显示和编辑目录
        outline_content = st.text_area(
            "目录编辑",
            value="\n".join(sample_outline),
            height=400,
            key="outline_editor",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("**操作**")
        
        if st.button("➕ 添加章节", use_container_width=True):
            st.info("添加章节功能待实现...")
        
        if st.button("➖ 删除章节", use_container_width=True):
            st.info("删除章节功能待实现...")
        
        if st.button("🔼 上移", use_container_width=True):
            st.info("上移功能待实现...")
        
        if st.button("🔽 下移", use_container_width=True):
            st.info("下移功能待实现...")
        
        st.markdown("---")
        
        if st.button("🔄 重新生成", use_container_width=True):
            st.info("重新生成功能待实现...")
    
    # 目录预览区域
    st.markdown("---")
    st.markdown("#### 👀 目录预览")
    
    # 将文本转换为列表显示
    outline_list = [line.strip() for line in outline_content.split('\n') if line.strip()]
    
    for item in outline_list:
        st.write(item)
    
    # 保存到session state
    st.session_state.outline_content = outline_content
    
    return {
        'outline': outline_list,
        'raw_content': outline_content
    }