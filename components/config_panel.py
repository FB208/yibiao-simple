import streamlit as st
import json
import os
import openai
from typing import List, Dict

# 配置文件路径 - 存储到用户家目录中
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ai_write_helper", "user_config.json")

def load_config() -> Dict:
    """从本地JSON文件加载配置"""
    config = {'api_key': '', 'base_url': '', 'model_name': 'gpt-3.5-turbo'}
    
    # 确保配置目录存在
    config_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir, exist_ok=True)
        except Exception as e:
            st.error(f"配置目录创建失败: {e}")
            return config
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                config.update(loaded_config)
        except Exception as e:
            st.error(f"配置加载失败: {e}")
    
    return config

def save_config(api_key: str, base_url: str, model_name: str) -> bool:
    """保存配置到本地JSON文件"""
    config = {
        'api_key': api_key,
        'base_url': base_url,
        'model_name': model_name
    }
    
    # 确保配置目录存在
    config_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir, exist_ok=True)
        except Exception as e:
            st.error(f"配置目录创建失败: {e}")
            return False
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"配置保存失败: {e}")
        return False

def get_available_models(api_key: str, base_url: str) -> List[str]:
    """获取可用的模型列表"""
    try:
        client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None
        )
        
        models = client.models.list()
        chat_models = []
        for model in models.data:
            model_id = model.id.lower()
            if any(keyword in model_id for keyword in ['gpt', 'claude', 'chat', 'llama', 'qwen', 'deepseek']):
                chat_models.append(model.id)
        
        return sorted(list(set(chat_models)))
    except Exception as e:
        st.error(f"获取模型列表失败: {str(e)}")
        return []

def render_config_panel(title: str = "AI写标书助手"):
    """渲染左侧配置面板"""
    with st.sidebar:
        # 大标题显示在配置面板顶部，减小上边距
        st.markdown(f"# {title}")
        st.markdown("---")
        
        st.header("⚙️ 基本配置")
        
        # 初始化session state（防御性编程）
        if 'config_loaded' not in st.session_state:
            st.session_state.config_loaded = False
        
        if 'api_key' not in st.session_state:
            st.session_state.api_key = ''
        
        if 'base_url' not in st.session_state:
            st.session_state.base_url = ''
        
        if 'model_name' not in st.session_state:
            st.session_state.model_name = 'gpt-3.5-turbo'
        
        # 只在首次加载时从文件读取配置
        if not st.session_state.config_loaded:
            config = load_config()
            st.session_state.api_key = config.get('api_key', '')
            st.session_state.base_url = config.get('base_url', '')
            st.session_state.model_name = config.get('model_name', 'gpt-3.5-turbo')
            st.session_state.config_loaded = True
        
        # 使用session state中的值作为默认值
        api_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.api_key,
            type="password",
            help="输入你的OpenAI API密钥"
        )
        
        base_url = st.text_input(
            "Base URL (可选)",
            value=st.session_state.base_url,
            help="如果使用代理或其他服务，请输入base URL"
        )
        
        # 模型配置
        st.subheader("🤖 模型配置")
        
        # 获取模型列表按钮
        if st.button("🔄 获取可用模型", key="get_models", use_container_width=True):
            if api_key:
                with st.spinner("正在获取模型列表..."):
                    models = get_available_models(api_key, base_url)
                    if models:
                        st.session_state.available_models = models
                        st.success(f"获取到 {len(models)} 个模型")
                        st.rerun()
                    else:
                        st.warning("获取模型列表失败，请手动输入模型名称")
            else:
                st.error("请先输入API Key")
        
        # 模型选择或输入
        if st.session_state.get('available_models'):
            model_name = st.selectbox(
                "选择模型",
                options=st.session_state.available_models,
                index=st.session_state.available_models.index(st.session_state.model_name) 
                      if st.session_state.model_name in st.session_state.available_models 
                      else 0
            )
        else:
            model_name = st.text_input(
                "模型名称",
                value=st.session_state.model_name,
                help="输入要使用的模型名称，如：gpt-3.5-turbo, gpt-4, gpt-4-turbo-preview等"
            )
        
        if st.button("💾 保存配置", use_container_width=True):
            if save_config(api_key, base_url, model_name):
                st.session_state.api_key = api_key
                st.session_state.base_url = base_url
                st.session_state.model_name = model_name
                
                # 清除OpenAI服务缓存，确保配置更改后立即生效
                try:
                    from services.openai_servce import clear_openai_service_cache
                    clear_openai_service_cache()
                except ImportError:
                    pass  # 如果服务模块不存在，忽略错误
                
                st.success("配置已保存到本地！")
                st.rerun()
            else:
                st.error("配置保存失败！")
        
        st.markdown("---")
        st.markdown("### 📋 使用说明")
        st.markdown("""
        1. 配置API密钥和Base URL
        2. 选择或输入模型名称
        3. 按步骤完成标书编写流程
        """)