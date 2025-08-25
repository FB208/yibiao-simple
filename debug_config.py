#!/usr/bin/env python3
"""
调试配置持久化的脚本
"""
import os
import json

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ai_write_helper", "user_config.json")

def debug_config():
    """调试配置功能"""
    print("🔍 调试配置持久化")
    print("=" * 50)
    
    # 检查配置文件是否存在
    print(f"配置文件路径: {os.path.abspath(CONFIG_FILE)}")
    print(f"配置文件存在: {os.path.exists(CONFIG_FILE)}")
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"当前配置: {config}")
        except Exception as e:
            print(f"读取配置失败: {e}")
    else:
        print("配置文件不存在，这是正常的首次使用")
    
    # 创建测试配置
    test_config = {
        'api_key': 'sk-test123456789',
        'base_url': 'https://api.openai.com/v1',
        'model_name': 'gpt-3.5-turbo'
    }
    
    print(f"\n创建测试配置: {test_config}")
    try:
        # 确保配置目录存在
        config_dir = os.path.dirname(CONFIG_FILE)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
            print(f"✅ 创建配置目录: {config_dir}")
            
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, ensure_ascii=False, indent=2)
        print("✅ 测试配置创建成功")
    except Exception as e:
        print(f"❌ 创建测试配置失败: {e}")

if __name__ == "__main__":
    debug_config()