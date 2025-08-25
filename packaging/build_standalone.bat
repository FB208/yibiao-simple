@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

echo ========================================
echo AI写标书助手 - 独立环境打包脚本
echo ========================================

echo.
echo 当前Python环境信息:
python --version 2>nul
if errorlevel 1 (
    echo 错误: 找不到Python，请确保Python已安装并在PATH中
    pause
    exit /b 1
)

where python
echo.

echo 检查必要依赖...
echo 正在检查: streamlit, pyinstaller, openai, python-docx...

python -c "
import sys
missing = []
try:
    import streamlit
    print('✓ streamlit 已安装')
except ImportError:
    missing.append('streamlit')
    print('✗ streamlit 缺失')

try:
    import PyInstaller
    print('✓ pyinstaller 已安装')
except ImportError:
    missing.append('pyinstaller')
    print('✗ pyinstaller 缺失')

try:
    import openai
    print('✓ openai 已安装')
except ImportError:
    missing.append('openai')
    print('✗ openai 缺失')

try:
    import docx
    print('✓ python-docx 已安装')
except ImportError:
    missing.append('python-docx')
    print('✗ python-docx 缺失')

try:
    import streamlit_option_menu
    print('✓ streamlit-option-menu 已安装')
except ImportError:
    missing.append('streamlit-option-menu')
    print('✗ streamlit-option-menu 缺失')

if missing:
    print(f'需要安装: {\" \".join(missing)}')
    sys.exit(1)
else:
    print('✓ 所有依赖检查通过')
"

if errorlevel 1 (
    echo.
    echo 安装缺失的依赖...
    pip install streamlit pyinstaller openai python-docx streamlit-option-menu PyPDF2 python-dotenv
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
    echo ✓ 依赖安装完成
)

echo.
echo 清理之前的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo 开始打包 (单文件模式)...
echo 这可能需要几分钟时间，请耐心等待...
echo.

pyinstaller --clean build_app.spec --log-level=WARN

echo.
echo ========================================
if exist "dist\AI写标书助手.exe" (
    echo ✓ 打包成功！
    echo ========================================
    
    echo 文件信息:
    echo 位置: %~dp0dist\AI写标书助手.exe
    
    for %%A in ("dist\AI写标书助手.exe") do (
        set /a size_mb=%%~zA/1024/1024
        echo 大小: !size_mb! MB
        echo 类型: 单文件可执行程序
    )
    
    echo.
    echo 使用说明:
    echo 1. 直接双击 dist\AI写标书助手.exe 启动
    echo 2. 或使用 启动AI写标书助手.bat
    echo 3. 无需安装Python环境即可运行
    echo 4. 可复制到任何Windows电脑使用
    
    echo.
    echo 快速测试启动...
    cd dist
    start /min "测试启动" "AI写标书助手.exe"
    timeout /t 3 /nobreak >nul
    taskkill /f /im "AI写标书助手.exe" >nul 2>&1
    echo ✓ 启动测试完成
    
) else (
    echo ✗ 打包失败
    echo ========================================
    echo 可能的原因:
    echo 1. 缺少必要依赖
    echo 2. build_app.spec 配置问题
    echo 3. 磁盘空间不足
    echo.
    echo 建议:
    echo 1. 检查上述错误信息
    echo 2. 手动运行: pyinstaller --clean build_app.spec
)

echo.
echo ========================================
pause