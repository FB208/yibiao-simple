"""
样式管理模块
用于集中管理应用的CSS样式
"""

import streamlit as st

def apply_custom_styles():
    """
    应用自定义CSS样式，优化页面布局和空间利用
    """
    st.markdown("""
<style>
    /* ===== 主要布局优化 ===== */
    /* 减少主内容区域的顶部和底部填充 */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: none !important;
    }
    
    /* 隐藏Streamlit的header以节省空间 */
    header[data-testid="stHeader"] {
        height: 0px !important;
        display: none !important;
    }
    
    /* 隐藏Streamlit的菜单按钮和footer */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    
    /* ===== 侧边栏优化 ===== */
    /* 优化侧边栏的间距和布局 */
    .css-1d391kg, .st-emotion-cache-1d391kg, [data-testid="stSidebar"] {
        padding-top: 0 !important;
    }
    
    /* 减少侧边栏标题的上方空间 */
    .sidebar .element-container:first-child {
        margin-top: 0 !important;
    }
    
    /* 减小侧边栏容器内部的填充 */
    [data-testid="stSidebarContent"] {
        padding-top: 0 !important;
    }
    
    /* 优化侧边栏中标题的边距 */
    .sidebar h1 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* 侧边栏中的第一个元素不要顶部边距 */
    section[data-testid="stSidebar"] .element-container:first-child {
        margin-top: 0 !important;
    }
    
    /* 侧边栏标题优化 */
    section[data-testid="stSidebar"] h1 {
        margin-top: 0.2rem !important;
        padding-top: 0 !important;
    }
    
    /* 进一步优化侧边栏内容的内边距 */
    section[data-testid="stSidebar"] > div {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* 更全面的侧边栏样式优化 */
    .css-17eq0hr, .css-1lcbmhc, .css-1d391kg,
    .st-emotion-cache-1d391kg, .st-emotion-cache-17eq0hr {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* 侧边栏内部的所有顶级元素 */
    .sidebar-content > div:first-child,
    [data-testid="stSidebarContent"] > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Streamlit 侧边栏的 CSS 类名可能会变化，这里尽量全面覆盖 */
    div[class*="stSidebar"], section[class*="stSidebar"] {
        padding-top: 0 !important;
    }
    
    div[class*="stSidebar"] > div:first-child,
    section[class*="stSidebar"] > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* ===== 间距优化 ===== */
    /* 减少元素间距 */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* 优化标题间距 */
    h1, h2, h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* 减少分割线间距 */
    hr {
        margin: 0.5rem 0 !important;
    }
    
    /* ===== 表单元素优化 ===== */
    .stSelectbox, .stTextInput, .stTextArea {
        margin-bottom: 0.5rem !important;
    }
    
    /* 优化按钮样式 */
    .stButton > button {
        width: 100%;
    }
    
    /* ===== 步骤条样式 ===== */
    .step-container {
        padding: 0.5rem 0;
    }
    
    /* ===== 文件上传组件优化 ===== */
    .stFileUploader {
        margin-bottom: 1rem !important;
    }
    
    /* ===== 响应式设计 ===== */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

def apply_theme_colors():
    """
    应用主题颜色方案
    """
    st.markdown("""
<style>
    /* ===== 主题颜色 ===== */
    :root {
        --primary-color: #FF6B6B;
        --secondary-color: #4ECDC4;
        --background-color: #F8F9FA;
        --text-color: #2C3E50;
    }
    
    /* 主按钮样式 */
    .stButton > button[kind="primary"] {
        background-color: var(--primary-color);
        border-color: var(--primary-color);
    }
    
    /* 成功信息样式 */
    .stSuccess {
        background-color: #D4EDDA;
        border-color: #C3E6CB;
        color: #155724;
    }
    
    /* 警告信息样式 */
    .stWarning {
        background-color: #FFF3CD;
        border-color: #FFEAA7;
        color: #856404;
    }
    
    /* 错误信息样式 */
    .stError {
        background-color: #F8D7DA;
        border-color: #F5C6CB;
        color: #721C24;
    }
</style>
""", unsafe_allow_html=True)
