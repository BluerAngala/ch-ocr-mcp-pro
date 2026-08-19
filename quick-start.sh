#!/bin/bash
# OCR MCP Pro - 快速启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "🚀 OCR MCP Pro 快速启动"
echo "=========================================="

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "📦 首次运行，正在安装依赖..."
    echo "   使用清华镜像加速..."
    python3 setup.py --mirror tsinghua
    echo ""
fi

# 检查依赖
echo "🔍 检查依赖..."
.venv/bin/python -c "import rapidocr_onnxruntime" 2>/dev/null || {
    echo "⚠️  依赖未完整安装，正在修复..."
    python3 setup.py --mirror tsinghua
}

echo ""
echo "✅ 环境就绪！"
echo ""
echo "📝 使用方法:"
echo "   1. 运行 OCR 服务器: ./run.sh"
echo "   2. 查看 MCP 配置: cat mcp_config.example.json"
echo "   3. 检查环境状态: python3 setup.py --check"
echo ""
echo "🔧 MCP 工具:"
echo "   - check_environment: 检查环境"
echo "   - install_dependencies: 安装依赖"
echo "   - list_engines: 列出引擎"
echo "   - ocr_image: 图片 OCR"
echo "   - ocr_pdf: PDF OCR"
echo "   - batch_ocr: 批量 OCR"
echo "   - compare_engines: 引擎对比"
echo "   - evaluate_accuracy: 精度评估"
echo ""
echo "=========================================="

# 如果有参数，运行指定命令
if [ "$1" = "--run" ] || [ "$1" = "-r" ]; then
    echo "🚀 启动 OCR 服务器..."
    exec .venv/bin/python index.py
elif [ "$1" = "--check" ] || [ "$1" = "-c" ]; then
    python3 setup.py --check
elif [ "$1" = "--install" ] || [ "$1" = "-i" ]; then
    python3 setup.py --mirror tsinghua
fi
