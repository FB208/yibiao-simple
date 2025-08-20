import streamlit as st
from typing import List, Tuple

def render_step_bar(steps: List[str], current_step: int):
    """
    渲染步骤条组件
    
    Args:
        steps: 步骤列表，每个元素是一个步骤名称
        current_step: 当前步骤的索引（从0开始）
    """
    
    st.markdown("""
    <style>
    .step-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 10px;
    }
    .step-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        position: relative;
    }
    .step-item:not(:last-child)::after {
        content: '';
        position: absolute;
        top: 20px;
        left: 50%;
        width: 100%;
        height: 2px;
        background-color: #dee2e6;
        z-index: 1;
        transform: translateX(-50%);
    }
    /* 确保步骤项内容正确对齐 */
    .step-item {
        text-align: center;
    }
    .step-item.completed:not(:last-child)::after {
        background-color: #28a745;
    }
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        z-index: 2;
        position: relative;
        margin-bottom: 8px;
    }
    .step-circle.completed {
        background-color: #28a745;
        color: white;
    }
    .step-circle.active {
        background-color: #007bff;
        color: white;
        border: 3px solid #0056b3;
    }
    .step-circle.pending {
        background-color: #dee2e6;
        color: #6c757d;
    }
    .step-label {
        font-size: 14px;
        font-weight: 500;
        text-align: center;
        color: #495057;
    }
    .step-label.active {
        color: #007bff;
        font-weight: bold;
    }
    .step-label.completed {
        color: #28a745;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 创建步骤条HTML
    steps_html = "<div class='step-container'>"
    
    for i, step_name in enumerate(steps):
        if i < current_step:
            status = "completed"
            circle_content = "✓"
        elif i == current_step:
            status = "active"
            circle_content = str(i + 1)
        else:
            status = "pending"
            circle_content = str(i + 1)
        
        # 使用单行字符串避免格式问题
        steps_html += f'<div class="step-item {status}"><div class="step-circle {status}">{circle_content}</div><div class="step-label {status}">{step_name}</div></div>'
    
    steps_html += "</div>"
    
    # 确保使用unsafe_allow_html=True参数
    st.markdown(steps_html, unsafe_allow_html=True)

def get_step_navigation(steps: List[str], current_step: int) -> Tuple[bool, bool]:
    """
    获取步骤导航按钮
    
    Args:
        steps: 步骤列表
        current_step: 当前步骤索引
    
    Returns:
        (上一步按钮是否被点击, 下一步按钮是否被点击)
    """
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    prev_clicked = False
    next_clicked = False
    
    with col1:
        if current_step > 0:
            if st.button("← 上一步", use_container_width=True):
                prev_clicked = True
    
    with col3:
        if current_step < len(steps) - 1:
            if st.button("下一步 →", use_container_width=True, type="primary"):
                next_clicked = True
    
    return prev_clicked, next_clicked