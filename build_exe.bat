@echo off
echo ========================================
echo 开始打包AI写标书助手为exe文件...
echo ========================================

echo.
echo 1. 清理之前的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo 2. 使用PyInstaller打包应用...
pyinstaller --clean build_app.spec

echo.
echo 3. 检查打包结果...
if exist "dist\AI写标书助手\AI写标书助手.exe" (
    echo ✓ 打包成功！
    echo ✓ 可执行文件位置: dist\AI写标书助手\AI写标书助手.exe
    echo.
    echo 使用说明:
    echo 1. 进入dist\AI写标书助手\目录
    echo 2. 双击AI写标书助手.exe启动应用
    echo 3. 浏览器会自动打开并显示应用界面
    echo.
) else (
    echo ✗ 打包失败，请检查错误信息
)

echo ========================================
echo 打包完成
echo ========================================
pause