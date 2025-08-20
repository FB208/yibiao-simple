import openai
import streamlit as st
from typing import Generator, Dict, Any
import json

class OpenAIService:
    """OpenAI服务类，提供流式和非流式请求功能"""
    
    def __init__(self, api_key: str, base_url: str = None, model_name: str = "gpt-3.5-turbo"):
        """
        初始化OpenAI服务
        
        Args:
            api_key: OpenAI API密钥
            base_url: 基础URL（可选，用于代理）
            model_name: 模型名称
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        
        # 初始化OpenAI客户端
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None
        )
    
    def stream_chat_completion(
        self, 
        messages: list, 
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Generator[str, None, None]:
        """
        流式聊天完成请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数，控制随机性
            max_tokens: 最大token数
            
        Yields:
            流式返回的文本片段
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"错误: {str(e)}"
    
    def analyze_document(self, file_content: str, analysis_type: str = "overview") -> Generator[str, None, None]:
        """
        分析文档内容
        
        Args:
            file_content: 文档内容
            analysis_type: 分析类型 ("overview" 或 "requirements")
            
        Yields:
            流式分析结果
        """
        if analysis_type == "overview":
            system_prompt = """你是一个专业的招标文件分析专家。请分析上传的招标文件，提取并总结项目概述信息。
            
请重点关注以下方面：
1. 项目名称和基本信息
2. 项目背景和目的
3. 项目规模和预算
4. 项目时间安排
5. 主要技术特点
6. 关键要求

工作要求：
1. 保持提取信息的全面性和准确性，尽量使用原文内容，不要自己编写
2. 只关注与项目实施有关的内容，不提取商务信息
3. 直接返回整理好的项目概述，除此之外不返回任何其他内容
"""
        else:  # requirements
            system_prompt = """你是一个专业的招标文件分析专家。请分析上传的招标文件，提取技术评分要求,为编写投标文件中的技术方案做准备。
            
请重点关注以下方面：
1. 理解技术评分的意思：用于编写、评比投标文件中技术标的标准，关注技术方案、实施计划、技术能力、质量控制、创新性等内容，避免混淆商务评分（资质、信誉、合同条款）和价格评分（报价金额）
2. 仅提取技术评分项及相关要求，不包括商务、价格及其他
3. 生成内容要确保是从招标文件中提取的，不要自己编写
4. 直接返回整理好的技术评分要求，除此之外不返回任何其他内容
"""
        analysis_type_cn = "项目概述" if analysis_type == "overview" else "技术评分要求"
        user_prompt = f"请分析以下招标文件内容，提取{analysis_type_cn}信息：\n\n{file_content}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 流式返回分析结果
        for chunk in self.stream_chat_completion(messages, temperature=0.3):
            yield chunk

def get_openai_service() -> OpenAIService:
    """
    获取OpenAI服务实例，使用缓存机制避免重复创建
    
    Returns:
        OpenAIService实例
    """
    # 获取当前配置
    api_key = st.session_state.get('api_key', '')
    base_url = st.session_state.get('base_url', '')
    model_name = st.session_state.get('model_name', 'gpt-3.5-turbo')
    
    if not api_key:
        raise ValueError("请先配置OpenAI API密钥")
    
    # 检查缓存的服务实例是否与当前配置匹配
    cached_service = st.session_state.get('openai_service_instance')
    if (cached_service and 
        cached_service.api_key == api_key and 
        cached_service.base_url == base_url and 
        cached_service.model_name == model_name):
        return cached_service
    
    # 创建新的服务实例并缓存
    new_service = OpenAIService(api_key, base_url, model_name)
    st.session_state.openai_service_instance = new_service
    
    return new_service

def clear_openai_service_cache():
    """清除OpenAI服务缓存"""
    if 'openai_service_instance' in st.session_state:
        del st.session_state.openai_service_instance 