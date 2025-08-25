#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
健壮的AI写标书助手启动器
绕过streamlit元数据检查问题
"""

import sys
import os
import threading
import time
import webbrowser
import socket
from pathlib import Path

def patch_streamlit_metadata():
    """修补streamlit元数据问题"""
    try:
        # 模拟streamlit版本信息
        import streamlit
        if not hasattr(streamlit, '__version__'):
            streamlit.__version__ = '1.48.1'
        
        # 修补importlib.metadata
        import importlib.metadata
        original_version = importlib.metadata.version
        original_distribution = importlib.metadata.distribution
        
        def patched_version(name):
            if name == 'streamlit':
                return '1.48.1'
            return original_version(name)
        
        def patched_distribution(name):
            if name == 'streamlit':
                # 创建一个最小的Distribution对象
                class MockDistribution:
                    def __init__(self, version):
                        self.version = version
                    
                    @property
                    def metadata(self):
                        return {'Version': self.version, 'Name': 'streamlit'}
                
                return MockDistribution('1.48.1')
            return original_distribution(name)
        
        importlib.metadata.version = patched_version
        importlib.metadata.distribution = patched_distribution
        
        print("Streamlit元数据修补成功")
        return True
        
    except Exception as e:
        print(f"元数据修补失败: {e}")
        return False

def find_free_port():
    """查找可用端口"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def run_streamlit_directly():
    """直接运行streamlit应用，不依赖CLI"""
    try:
        # 获取应用目录
        if hasattr(sys, '_MEIPASS'):
            app_dir = sys._MEIPASS
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        os.chdir(app_dir)
        main_app_path = os.path.join(app_dir, "main_app.py")
        
        if not os.path.exists(main_app_path):
            print(f"错误：找不到main_app.py文件: {main_app_path}")
            return False
        
        # 修补元数据
        patch_streamlit_metadata()
        
        # 查找可用端口
        port = find_free_port()
        print(f"使用端口: {port}")
        
        # 设置环境变量
        os.environ.update({
            'STREAMLIT_SERVER_PORT': str(port),
            'STREAMLIT_SERVER_HEADLESS': 'true',
            'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
            'STREAMLIT_SERVER_FILE_WATCHER_TYPE': 'none'
        })
        
        # 延迟打开浏览器
        def open_browser():
            time.sleep(8)  # 给更多时间启动
            
            # 检查多个可能的端口
            ports_to_try = [port, 8501, 3000]
            for test_port in ports_to_try:
                try:
                    import urllib.request
                    url = f"http://localhost:{test_port}"
                    response = urllib.request.urlopen(url, timeout=2)
                    if response.getcode() == 200:
                        print(f"应用运行在端口 {test_port}")
                        print(f"在浏览器中打开: {url}")
                        webbrowser.open(url)
                        return
                except Exception:
                    continue
            
            # 如果都不行，尝试原端口
            url = f"http://localhost:{port}"
            print(f"尝试在浏览器中打开: {url}")
            webbrowser.open(url)
        
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        print("\n" + "="*50)
        print("AI写标书助手启动中...")
        print(f"访问地址: http://localhost:{port}")
        print("请等待浏览器自动打开")
        print("="*50 + "\n")
        
        # 方法1: 尝试使用streamlit web bootstrap
        try:
            import streamlit.web.bootstrap as bootstrap
            import streamlit.config as config
            print("尝试使用bootstrap方式启动...")
            
            # 重置并设置配置
            config.set_option('server.port', port)
            config.set_option('server.headless', True)
            config.set_option('server.fileWatcherType', 'none')
            config.set_option('browser.gatherUsageStats', False)
            config.set_option('global.developmentMode', False)
            config.set_option('server.enableCORS', False)
            config.set_option('server.enableXsrfProtection', False)
            
            print(f"配置端口: {port}")
            
            # 配置启动参数
            flag_options = {
                'server_port': port,
                'server_headless': True, 
                'server_fileWatcherType': 'none',
                'browser_gatherUsageStats': False,
                'global_developmentMode': False
            }
            
            bootstrap.run(main_app_path, '', [], flag_options)
            return True
            
        except Exception as e:
            print(f"Bootstrap启动失败: {e}")
        
        # 方法2: 直接执行main_app.py  
        try:
            print("尝试直接运行main_app.py...")
            
            # 添加当前目录到Python路径
            if app_dir not in sys.path:
                sys.path.insert(0, app_dir)
            
            # 设置streamlit配置
            import streamlit as st
            
            # 配置页面
            st.set_page_config(
                page_title="AI写标书助手",
                page_icon="📝", 
                layout="wide",
                initial_sidebar_state="expanded"
            )
            
            # 执行main_app
            with open(main_app_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # 创建一个新的全局命名空间
            globals_dict = {
                '__name__': '__main__',
                '__file__': main_app_path,
                '__package__': None
            }
            
            exec(code, globals_dict)
            return True
            
        except Exception as e:
            print(f"直接运行失败: {e}")
            import traceback
            traceback.print_exc()
        
        return False
        
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    try:
        print("=== AI写标书助手 健壮启动器 ===")
        
        # 防重复启动检查
        lock_file = os.path.join(os.path.expanduser("~"), ".ai_write_helper.lock")
        
        if os.path.exists(lock_file):
            print("检测到应用可能正在运行，强制启动...")
            # 删除旧的锁文件
            os.remove(lock_file)
        
        # 创建锁文件
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        
        try:
            success = run_streamlit_directly()
            if not success:
                print("所有启动方法都失败了")
                print("程序将在3秒后自动退出...")
                time.sleep(3)
        finally:
            # 清理锁文件
            if os.path.exists(lock_file):
                os.remove(lock_file)
                
    except KeyboardInterrupt:
        print("\n用户中断，正在退出...")
    except Exception as e:
        print(f"程序异常: {e}")
        print("程序将在3秒后自动退出...")
        time.sleep(3)

if __name__ == "__main__":
    main()