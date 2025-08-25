import streamlit as st
from components.config_panel import render_config_panel
from components.step_bar import render_step_bar, get_step_navigation
from components.styles import apply_custom_styles, apply_theme_colors
from page_modules.document_analysis import render_document_analysis_page
from page_modules.outline_edit import render_outline_edit_page
from page_modules.content_edit import render_content_edit_page

# 页面配置
st.set_page_config(
    page_title="AI写标书助手",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用自定义样式
apply_custom_styles()
apply_theme_colors()

def main():
    """主应用函数"""
    
    # 初始化所有必要的session state变量
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    
    if 'config_loaded' not in st.session_state:
        st.session_state.config_loaded = False
    
    # 来自document_analysis.py的变量
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    if 'file_content' not in st.session_state:
        st.session_state.file_content = ''
    if 'start_analysis' not in st.session_state:
        st.session_state.start_analysis = False
    if 'project_overview' not in st.session_state:
        st.session_state.project_overview = ''
    if 'tech_requirements' not in st.session_state:
        st.session_state.tech_requirements = ''
    
    # 来自config_panel.py的变量  
    if 'base_url' not in st.session_state:
        st.session_state.base_url = ''
    if 'model_name' not in st.session_state:
        st.session_state.model_name = 'gpt-3.5-turbo'
        
    # 来自outline_edit.py的变量
    if 'outline_data' not in st.session_state:
        st.session_state.outline_data = None
    if 'outline_generated' not in st.session_state:
        st.session_state.outline_generated = False
    if 'generating_outline' not in st.session_state:
        st.session_state.generating_outline = False

    # 来自content_edit.py的变量
    if 'chapter_contents' not in st.session_state:
        st.session_state.chapter_contents = {}
    if 'selected_chapter' not in st.session_state:
        st.session_state.selected_chapter = ''
    
    # 定义步骤
    steps = ["标书解析", "目录编辑", "正文编辑"]
    
    # 渲染左侧配置面板（包含大标题）
    render_config_panel("AI写标书助手")
    
    # 渲染步骤条
    render_step_bar(steps, st.session_state.current_step)
    st.session_state.current_step=2
    # 渲染当前页面内容
    if st.session_state.current_step == 0:
        # 标书解析页面
        page_data = render_document_analysis_page()
        
    elif st.session_state.current_step == 1:
        # 目录编辑页面
        page_data = render_outline_edit_page()
        
    elif st.session_state.current_step == 2:
        # 正文编辑页面
        page_data = render_content_edit_page()
    
    # 步骤导航
    prev_clicked, next_clicked = get_step_navigation(steps, st.session_state.current_step)
    
    # 处理步骤导航
    if prev_clicked and st.session_state.current_step > 0:
        st.session_state.current_step -= 1
        st.rerun()
    
    if next_clicked and st.session_state.current_step < len(steps) - 1:
        st.session_state.current_step += 1
        st.rerun()

if __name__ == "__main__":
    main()