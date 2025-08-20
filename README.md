# AI写标书助手

一个基于Streamlit和OpenAI API的智能标书写作助手，可以自动解析招标文件并生成标书内容。

## 功能特性

- 📄 支持Word (.docx) 和PDF (.pdf) 格式的招标文件上传
- 🤖 使用OpenAI API智能解析招标文件
- 📋 自动提取项目概述和技术评分要求
- ⚙️ 支持自定义API配置（API Key和Base URL）
- 💾 浏览器缓存配置信息
- 🖥️ 友好的Web界面

## 安装和运行

### 开发环境运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
streamlit run main_app.py
```

### 打包成exe文件

1. 运行构建脚本：
```bash
python build.py
```

2. 构建完成后，exe文件将位于 `dist` 目录中

3. 双击exe文件即可运行，会自动打开浏览器

## 使用说明

1. **配置设置**：在左侧面板输入OpenAI API Key和Base URL（可选）
2. **上传文件**：上传招标文件（支持Word和PDF格式）
3. **解析文档**：点击"解析文档"按钮，AI将自动提取关键信息
4. **编辑结果**：可以手动修改解析出的项目概述和技术评分要求
5. **生成目录**：点击"生成目录"进入下一步（待开发）

## 技术栈

- **前端框架**：Streamlit
- **AI服务**：OpenAI API
- **文档处理**：python-docx, PyPDF2
- **打包工具**：PyInstaller

## 项目结构

```
├── app.py              # 主应用文件
├── run_app.py          # 启动脚本
├── build.py            # 构建脚本
├── requirements.txt    # 依赖列表
└── README.md          # 说明文档
```

## 注意事项

- 需要有效的OpenAI API Key才能使用文档解析功能
- 确保网络连接正常，能够访问OpenAI API
- 支持的文件格式：.docx, .pdf
- 建议使用Chrome或Edge浏览器以获得最佳体验