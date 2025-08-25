@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

REM 切换到项目根目录
cd /d "%~dp0\.."

echo ========================================
echo 开始打包AI写标书助手为单文件exe...
echo ========================================

echo.
echo 当前工作目录: %cd%
echo.
echo 1. 激活conda base环境...
call conda activate base
if errorlevel 1 (
    echo 警告: conda环境激活失败，尝试使用当前环境
    echo 如果打包失败，请手动执行: conda activate base
    echo.
)

echo.
echo 2. 检查必要依赖...
python -c "import streamlit, pyinstaller; print('依赖检查通过')" 2>nul
if errorlevel 1 (
    echo 安装必要依赖...
    pip install pyinstaller streamlit
)

echo.
echo 3. 清理之前的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo 4. 使用优化后的PyInstaller配置打包...
echo    单文件模式 + 体积优化 + 移除不必要依赖
pyinstaller --clean packaging\build_app.spec --log-level=WARN

echo.
echo 5. 检查打包结果...
if exist "dist\AI写标书助手.exe" (
    echo 打包成功！
    echo 可执行文件位置: dist\AI写标书助手.exe
    echo.
    for %%A in ("dist\AI写标书助手.exe") do (
        echo 文件大小: %%~zA 字节
        set /a size_mb=%%~zA/1024/1024
        echo 约等于: !size_mb! MB
    )
    echo.
    echo 使用说明:
    echo 1. 直接双击 dist\AI写标书助手.exe 启动
    echo 2. 或使用提供的 启动AI写标书助手.bat
    echo 3. 程序启动后会自动打开浏览器
    echo 4. 单文件无需额外依赖，可直接分发
    echo.
) else (
    echo 打包失败，请检查错误信息
)

echo ========================================
echo 打包完成
echo ========================================
pause