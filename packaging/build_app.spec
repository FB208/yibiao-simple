# -*- mode: python ; coding: utf-8 -*-
import streamlit as st
import os

# 获取项目根目录（当前工作目录）
project_root = os.getcwd()

# 优化后的单文件打包配置
a = Analysis(
    [os.path.join(project_root, 'robust_launcher.py')],
    pathex=[project_root],
    binaries=[],
    datas=[
        # 添加必要的Streamlit文件和元数据
        (st.__path__[0] + '/static', './streamlit/static'),
        (st.__path__[0] + '/runtime', './streamlit/runtime'),
        (st.__path__[0] + '/web', './streamlit/web'),
        # 添加项目相关文件
        (os.path.join(project_root, 'components'), 'components'),
        (os.path.join(project_root, 'page_modules'), 'page_modules'),
        (os.path.join(project_root, 'services'), 'services'),
        (os.path.join(project_root, 'main_app.py'), '.'),
    ],
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'streamlit.web.bootstrap',
        'streamlit.runtime.scriptrunner.script_runner',
        'streamlit.logger',
        'streamlit.runtime.caching.hashing',
        'streamlit.components.v1.components',
        'streamlit.runtime.state.session_state',
        'streamlit.web.server.server',
        'streamlit.runtime.app_session',
        'streamlit.config',
        'streamlit_option_menu',
        'openai',
        'docx',
        'PyPDF2',
        'dotenv',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'threading',
        'webbrowser',
        'socket',
        'pathlib',
        'urllib.request',
        'importlib.metadata',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # 排除不需要的包以减小体积
    excludes=[
        'matplotlib',
        'scipy',
        'sklearn',
        'tensorflow',
        'torch',
        'jupyter',
        'IPython',
        'pytest',
        'setuptools',
        'wheel',
        'pip',
        'altair',
        'numpy.random._examples',
        'pandas.tests',
        'streamlit.testing',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 修改为单文件模式
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
    strip=False,  # 禁用strip避免streamlit问题
    upx=True,   # 启用UPX压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)