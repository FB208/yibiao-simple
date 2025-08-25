@echo off
echo 快速打包AI写标书助手...

REM 确保必要依赖存在
pip install --quiet pyinstaller streamlit openai python-docx streamlit-option-menu PyPDF2 python-dotenv

REM 清理并打包
if exist "build" rmdir /s /q "build" >nul 2>&1
if exist "dist" rmdir /s /q "dist" >nul 2>&1

echo 正在打包...
pyinstaller --clean build_app.spec --log-level=ERROR

if exist "dist\AI写标书助手.exe" (
    echo 打包成功! 文件位置: dist\AI写标书助手.exe
) else (
    echo 打包失败!
)
pause