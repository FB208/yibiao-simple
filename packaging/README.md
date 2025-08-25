# 打包说明

本文件夹包含AI写标书助手的所有打包相关文件。

## 📁 文件说明

### 打包脚本
- **`build_standalone.bat`** - 推荐使用的独立打包脚本
  - ✅ 无需虚拟环境
  - ✅ 自动检查和安装依赖
  - ✅ 详细的进度显示和错误处理
  
- **`quick_build.bat`** - 快速打包脚本
  - ⚡ 最简洁版本
  - ⚡ 静默安装依赖
  
### 配置文件
- **`build_app.spec`** - PyInstaller配置文件
  - 单文件打包模式
  - 体积优化配置
  - 路径自动调整

## 🚀 使用方法

### 方法一：推荐使用（详细版）
```bash
双击运行: build_standalone.bat
```

### 方法二：快速打包
```bash
双击运行: quick_build.bat
```

### 方法三：手动打包
```bash
# 在项目根目录执行
pyinstaller --clean packaging\build_app.spec
```

## 📋 打包要求

### 必需依赖
- Python 3.7+
- streamlit
- pyinstaller
- openai
- python-docx
- streamlit-option-menu
- PyPDF2
- python-dotenv

### 系统要求
- Windows 10/11
- 至少4GB可用磁盘空间
- 足够的内存（推荐8GB+）

## 📦 输出说明

打包成功后会在项目根目录的 `dist` 文件夹中生成：
- `AI写标书助手.exe` - 单文件可执行程序（约100MB）

## ⚠️ 常见问题

### 1. 依赖缺失
如果提示缺少依赖，脚本会自动安装。如果自动安装失败，请手动执行：
```bash
pip install streamlit pyinstaller openai python-docx streamlit-option-menu PyPDF2 python-dotenv
```

### 2. 打包失败
- 确保在项目根目录运行
- 检查磁盘空间是否足够
- 确保没有杀毒软件干扰

### 3. 程序无法启动
- 确保目标机器是Windows系统
- 检查是否被杀毒软件拦截
- 尝试以管理员身份运行

## 📝 更新日志

- **v1.2** - 添加packaging文件夹，统一管理打包文件
- **v1.1** - 优化为单文件打包，减小体积到100MB
- **v1.0** - 初始版本