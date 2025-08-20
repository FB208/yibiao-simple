"""
启动脚本，用于在exe中运行Streamlit应用
"""
import subprocess
import sys
import os
import webbrowser
import time
import threading
from pathlib import Path

def open_browser():
    """延迟打开浏览器"""
    time.sleep(3)  # 等待服务器启动
    webbrowser.open('http://localhost:8501')

def main():
    """主函数"""
    # 获取当前脚本所在目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        app_dir = Path(sys.executable).parent
    else:
        # 如果是开发环境
        app_dir = Path(__file__).parent
    
    # 切换到应用目录
    os.chdir(app_dir)
    
    # 启动浏览器线程
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动Streamlit应用
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port=8501',
            '--server.address=localhost',
            '--server.headless=true',
            '--browser.gatherUsageStats=false'
        ])
    except KeyboardInterrupt:
        print("应用已关闭")
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()