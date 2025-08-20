import streamlit as st
from typing import Dict, List

def render_content_edit_page() -> Dict:
    """
    渲染正文编辑页面
    
    Returns:
        包含正文数据的字典
    """
    
    st.header("📝 正文编辑")
    st.markdown("### 第三步：编写和完善标书正文内容")
    
    # 章节选择器
    st.markdown("#### 📖 选择要编辑的章节")
    
    # 示例章节列表
    chapters = [
        "1. 项目概述",
        "2. 技术方案", 
        "3. 实施方案",
        "4. 质量保障",
        "5. 服务支持"
    ]
    
    selected_chapter = st.selectbox("选择章节", chapters, key="chapter_selector")
    
    # 章节内容编辑区域
    st.markdown(f"#### ✏️ 编辑 {selected_chapter}")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 根据选择的章节提供示例内容
        sample_content = get_sample_content(selected_chapter)
        
        chapter_content = st.text_area(
            f"{selected_chapter} 内容",
            value=sample_content,
            height=400,
            key=f"content_{selected_chapter}",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("**工具**")
        
        if st.button("🤖 AI生成", use_container_width=True):
            st.info("AI生成功能待实现...")
        
        if st.button("🔄 优化内容", use_container_width=True):
            st.info("内容优化功能待实现...")
        
        if st.button("📋 复制模板", use_container_width=True):
            st.info("复制模板功能待实现...")
        
        st.markdown("---")
        
        if st.button("💾 保存章节", use_container_width=True):
            st.success(f"章节 {selected_chapter} 已保存")
    
    # 进度显示
    st.markdown("---")
    st.markdown("#### 📊 编辑进度")
    
    progress_data = {
        "项目概述": 80,
        "技术方案": 60,
        "实施方案": 40,
        "质量保障": 20,
        "服务支持": 10
    }
    
    for chapter, progress in progress_data.items():
        st.write(f"{chapter}: {progress}%")
        st.progress(progress)
    
    # 保存所有章节内容
    if 'chapter_contents' not in st.session_state:
        st.session_state.chapter_contents = {}
    
    st.session_state.chapter_contents[selected_chapter] = chapter_content
    st.session_state.selected_chapter = selected_chapter
    
    return {
        'selected_chapter': selected_chapter,
        'chapter_content': chapter_content,
        'all_contents': st.session_state.chapter_contents
    }

def get_sample_content(chapter: str) -> str:
    """获取章节的示例内容"""
    
    sample_contents = {
        "1. 项目概述": """
1.1 项目背景
本项目旨在通过先进的信息技术手段，提升企业运营效率和管理水平。

1.2 项目目标
- 建立统一的信息化管理平台
- 实现业务流程的标准化和自动化
- 提高数据处理和分析能力
- 降低运营成本，提升服务质量

1.3 项目范围
本项目涵盖企业内部的各个业务部门，包括但不限于销售、采购、库存、财务、人力资源等核心模块。
        """,
        
        "2. 技术方案": """
2.1 总体架构
采用微服务架构设计，确保系统的可扩展性和高可用性。前端采用React框架，后端基于Spring Cloud构建。

2.2 技术路线
- 前端技术：React + TypeScript + Ant Design
- 后端技术：Spring Boot + Spring Cloud + MyBatis
- 数据库：MySQL + Redis
- 消息队列：RabbitMQ
- 容器化：Docker + Kubernetes

2.3 关键技术
- 分布式事务处理
- 高并发数据访问
- 实时数据同步
- 安全认证与授权
        """,
        
        "3. 实施方案": """
3.1 实施计划
项目分为四个阶段实施：
- 第一阶段：需求调研与系统设计（2个月）
- 第二阶段：系统开发与测试（4个月）
- 第三阶段：试点运行与优化（2个月）
- 第四阶段：全面推广与维护（持续）

3.2 人员配置
- 项目经理：1人
- 系统架构师：2人
- 前端开发工程师：3人
- 后端开发工程师：4人
- 测试工程师：2人
- 运维工程师：1人

3.3 进度安排
详细的甘特图将在项目启动后制定，确保各阶段任务按时完成。
        """,
        
        "4. 质量保障": """
4.1 质量标准
严格按照ISO 9001质量管理体系执行，确保交付产品符合行业标准和客户要求。

4.2 控制措施
- 代码审查：每个功能模块完成后进行代码审查
- 单元测试：开发过程中必须完成单元测试，覆盖率不低于80%
- 集成测试：系统模块集成后进行全面的集成测试
- 用户验收测试：客户参与最终验收测试

4.3 验收标准
- 功能完整性：所有需求功能点100%实现
- 性能指标：系统响应时间不超过2秒
- 稳定性：系统可用性达到99.9%
- 安全性：通过第三方安全测试
        """,
        
        "5. 服务支持": """
5.1 售后服务
提供7×24小时技术支持服务，包括电话支持、邮件支持和现场支持。

5.2 技术支持
- 系统维护：定期系统检查和维护
- 故障处理：4小时内响应，24小时内解决
- 升级服务：提供系统功能升级和技术更新

5.3 培训计划
- 管理员培训：系统管理和维护培训
- 用户培训：最终用户操作培训
- 培训材料：提供完整的培训手册和视频教程
        """
    }
    
    return sample_contents.get(chapter, "章节内容待编辑...")