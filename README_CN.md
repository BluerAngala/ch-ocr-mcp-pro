# CH OCR MCP Pro - 多引擎 OCR 服务器

基于 [Prekzursil 的 ocr-mcp](https://github.com/Prekzursil/abbyy-finereader-ocr-mcp) 改造，增加了**自动安装依赖**和**国内镜像加速**功能。

> 🇨🇳 专为中国用户优化，支持国内镜像加速安装

## ✨ 新增功能

| 功能 | 说明 |
|------|------|
| 🔧 自动安装 | `setup.py` 一键安装所有依赖 |
| 🚀 国内镜像 | 支持清华/阿里/华为等镜像加速 |
| 📦 依赖检查 | 启动时自动检查并提示缺失依赖 |
| 🛠️ MCP 工具 | 新增 `check_environment` 和 `install_dependencies` 工具 |

## 🚀 快速开始

### 方式一：自动安装（推荐）

```bash
# 克隆项目
git clone https://github.com/BluerAngala/ch-ocr-mcp-pro.git
cd ch-ocr-mcp-pro

# 使用国内镜像自动安装
python setup.py --mirror tsinghua

# 或使用阿里镜像
python setup.py --mirror aliyun
```

### 方式二：手动安装

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 使用镜像安装
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ \
    rapidocr-onnxruntime onnxruntime Pillow numpy pymupdf jiwer \
    opencv-python-headless pytesseract pyperclip
```

## 🛠️ MCP 工具列表

| 工具 | 功能 |
|------|------|
| `check_environment` | 检查环境和依赖状态 |
| `install_dependencies` | 自动安装依赖（支持镜像） |
| `list_engines` | 列出可用 OCR 引擎 |
| `ocr_image` | 图片 OCR 识别 |
| `ocr_pdf` | PDF OCR 识别 |
| `batch_ocr` | 批量 OCR |
| `compare_engines` | 多引擎对比 |
| `evaluate_accuracy` | 精度评估（CER/WER） |

## 📋 配置 MCP

运行 `setup.py` 后会自动生成 `mcp_config.example.json`，直接复制到你的 AI工具配置中即可。

### Claude Desktop

```json
{
  "mcpServers": {
    "ch-ocr": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "ocr_mcp"],
      "env": {
        "PYTHONUTF8": "1",
        "PYTHONUNBUFFERED": "1",
        "PYTHONPATH": "/path/to/ch-ocr-mcp-pro/src"
      }
    }
  }
}
```

### VS Code Copilot

```json
{
  "github.copilot.chat.mcp.servers": {
    "ch-ocr": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "ocr_mcp"],
      "env": {
        "PYTHONPATH": "/path/to/ch-ocr-mcp-pro/src"
      }
    }
  }
}
```

### Codex

```toml
[mcp_servers.ch-ocr]
command = "/path/to/.venv/bin/python"
args = ["-m", "ocr_mcp"]
startup_timeout_sec = 60
tool_timeout_sec = 300

[mcp_servers.ch-ocr.env]
PYTHONUTF8 = "1"
PYTHONUNBUFFERED = "1"
PYTHONPATH = "/path/to/ch-ocr-mcp-pro/src"
```

## 🔍 使用示例

```
> 检查一下我的环境是否就绪
  → check_environment()

> 帮我安装依赖，用清华镜像
  → install_dependencies(mirror="tsinghua")

> OCR 这张图片
  → ocr_image("/path/to/image.png")

> 对比哪个引擎效果最好
  → compare_engines("/path/to/image.png")

> 评估 OCR 准确率
  → evaluate_accuracy("/path/to/truth.txt", ocr_path="/path/to/image.png")
```

## 🌐 支持的镜像源

| 名称 | 地址 |
|------|------|
| `tsinghua` | https://pypi.tuna.tsinghua.edu.cn/simple/ |
| `aliyun` | https://mirrors.aliyun.com/pypi/simple/ |
| `ustc` | https://pypi.mirrors.ustc.edu.cn/simple/ |
| `huawei` | https://repo.huaweicloud.com/repository/pypi/simple/ |

也可以传入自定义镜像 URL。

## 🔐 安全配置

限制 OCR 可访问的目录：

```bash
# Linux/Mac
export OCR_MCP_ALLOWED_DIRS="/path/to/images:/path/to/documents"

# Windows
set OCR_MCP_ALLOWED_DIRS=D:\images;D:\documents
```

## 📊 OCR 引擎对比

| 引擎 | 特点 | 需要安装 |
|------|------|----------|
| **RapidOCR** | 默认引擎，本地运行，无需 GPU | ✅ 自动 |
| **Tesseract** | Google 引擎，多语言支持 | 需单独安装 |
| **ABBYY FineReader** | 最高精度，需要付费授权 | 需单独安装 |

## 🧪 开发测试

```bash
# 安装测试依赖
pip install -e ".[test]"

# 运行测试
pytest
```

## 📄 许可证

MIT License

## 🙏 致谢

- [RapidOCR](https://github.com/RapidAI/RapidOCR)
- [Tesseract](https://github.com/tesseract-ocr/tesseract)
- [ABBYY FineReader](https://pdf.abbyy.com/)
- [原项目作者 Prekzursil](https://github.com/Prekzursil/abbyy-finereader-ocr-mcp)
