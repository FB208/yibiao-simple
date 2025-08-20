"""
构建脚本，用于将Streamlit应用打包成exe文件
"""
import os
import subprocess
import sys

def install_requirements():
    """安装依赖"""
    print("安装依赖包...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_spec_file():
    """创建PyInstaller规格文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('venv/Lib/site-packages/streamlit/static', 'streamlit/static'),
        ('venv/Lib/site-packages/streamlit/runtime', 'streamlit/runtime'),
    ],
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'streamlit.runtime.scriptrunner.script_runner',
        'streamlit.runtime.state',
        'streamlit.runtime.uploaded_file_manager',
        'openai',
        'docx',
        'PyPDF2',
        'altair',
        'plotly',
        'PIL',
        'numpy',
        'pandas',
        'pyarrow',
        'pydeck',
        'tornado',
        'validators',
        'watchdog',
        'click',
        'toml',
        'tzlocal',
        'packaging',
        'gitpython',
        'pympler',
        'semver',
        'rich',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI写标书助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # 如果有图标文件的话
)
'''
    
    with open('app.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    subprocess.run(['pyinstaller', '--clean', 'app.spec'])

if __name__ == "__main__":
    print("开始构建AI写标书助手...")
    install_requirements()
    create_spec_file()
    build_exe()
    print("构建完成！exe文件位于dist目录中。")