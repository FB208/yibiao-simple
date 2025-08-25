@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

REM 切换到项目根目录
cd /d "%~dp0\.."

echo ========================================
echo AI写标书助手 - Conda环境打包脚本
echo ========================================
echo.
echo 当前工作目录: %cd%
echo.
echo 请选择要使用的conda环境:
echo 1. base (默认)
echo 2. 其他环境（手动输入）
echo 3. 跳过环境激活（使用当前环境）
echo.
set /p choice=请输入选择 (1-3): 

if "%choice%"=="1" (
    set env_name=base
) else if "%choice%"=="2" (
    set /p env_name=请输入环境名称: 
) else if "%choice%"=="3" (
    set env_name=
) else (
    echo 无效选择，使用默认base环境
    set env_name=base
)

echo.
if not "%env_name%"=="" (
    echo 激活conda环境: %env_name%
    call conda activate %env_name%
    if errorlevel 1 (
        echo 错误: 无法激活环境 %env_name%
        echo 请检查环境是否存在
        pause
        exit /b 1
    )
    echo 当前Python路径: 
    where python
    echo.
)

echo 检查必要依赖...
python -c "import streamlit, pyinstaller; print('✓ 依赖检查通过')" 2>nul
if errorlevel 1 (
    echo 缺少必要依赖，正在安装...
    pip install pyinstaller streamlit
    echo.
)

echo 清理构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo 开始打包...
pyinstaller --clean packaging\build_app.spec --log-level=WARN

echo.
if exist "dist\AI写标书助手.exe" (
    echo ========================================
    echo ✓ 打包成功！
    echo ========================================
    echo 文件位置: dist\AI写标书助手.exe
    
    for %%A in ("dist\AI写标书助手.exe") do (
        set /a size_mb=%%~zA/1024/1024
        echo 文件大小: !size_mb! MB
    )
    
    echo.
    echo 测试启动...
    cd dist
    timeout 5 "AI写标书助手.exe" >nul 2>&1 & taskkill /f /im "AI写标书助手.exe" >nul 2>&1
    if errorlevel 1 (
        echo ⚠ 程序可能无法正常启动，请手动测试
    ) else (
        echo ✓ 程序启动测试通过
    )
    
) else (
    echo ========================================
    echo ✗ 打包失败
    echo ========================================
    echo 请检查上面的错误信息
)

echo.
pause