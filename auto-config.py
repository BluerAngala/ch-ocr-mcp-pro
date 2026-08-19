#!/usr/bin/env python3
"""自动安装脚本 - 安装依赖并输出配置信息

使用方法:
    python auto-config.py                # 安装依赖并输出配置
    python auto-config.py --mirror tsinghua  # 使用国内镜像
    python auto-config.py --check        # 仅检查环境
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path


def get_project_dir() -> Path:
    """获取项目目录"""
    return Path(__file__).parent.resolve()


def get_venv_python(project_dir: Path) -> str:
    """获取虚拟环境 Python 路径"""
    venv_dir = project_dir / ".venv"
    if platform.system() == "Windows":
        return str(venv_dir / "Scripts" / "python.exe")
    return str(venv_dir / "bin" / "python")


def get_mcp_config(project_dir: Path) -> dict:
    """生成 MCP 配置"""
    python_path = get_venv_python(project_dir)
    src_dir = str(project_dir / "src")
    
    return {
        "mcpServers": {
            "ch-ocr": {
                "command": python_path,
                "args": ["-m", "ocr_mcp"],
                "env": {
                    "PYTHONUTF8": "1",
                    "PYTHONUNBUFFERED": "1",
                    "PYTHONPATH": src_dir
                }
            }
        }
    }


def check_environment(project_dir: Path) -> dict:
    """检查环境状态"""
    venv_dir = project_dir / ".venv"
    python_path = get_venv_python(project_dir)
    
    status = {
        "project_dir": str(project_dir),
        "venv_exists": venv_dir.exists(),
        "python_exists": Path(python_path).exists() if venv_dir.exists() else False,
        "python_path": python_path if venv_dir.exists() else None,
    }
    
    if status["python_exists"]:
        try:
            result = subprocess.run(
                [python_path, "-c", "import rapidocr; print('ok')"],
                capture_output=True, text=True, timeout=10
            )
            status["rapidocr_installed"] = result.returncode == 0
        except Exception:
            status["rapidocr_installed"] = False
    else:
        status["rapidocr_installed"] = False
    
    return status


def main():
    parser = argparse.ArgumentParser(description="CH OCR MCP Pro 自动安装")
    parser.add_argument("--mirror", "-m", nargs="?", const="tsinghua",
                       help="使用国内镜像 (tsinghua/aliyun/ustc/huawei)")
    parser.add_argument("--check", "-c", action="store_true",
                       help="仅检查环境状态")
    parser.add_argument("--output-json", action="store_true",
                       help="输出 JSON 格式（供 AI 读取）")
    args = parser.parse_args()
    
    project_dir = get_project_dir()
    
    if args.output_json:
        # JSON 输出模式，供 AI 读取
        status = check_environment(project_dir)
        if status["venv_exists"] and status["rapidocr_installed"]:
            config = get_mcp_config(project_dir)
            output = {
                "status": "ready",
                "config": config,
                "project_dir": str(project_dir),
            }
        else:
            output = {
                "status": "need_install",
                "project_dir": str(project_dir),
                "install_command": f"cd {project_dir} && python3 setup.py --mirror tsinghua",
                "venv_exists": status["venv_exists"],
                "rapidocr_installed": status["rapidocr_installed"],
            }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return
    
    # 普通输出模式
    print("=" * 50)
    print("🚀 CH OCR MCP Pro 自动安装")
    print("=" * 50)
    
    status = check_environment(project_dir)
    
    print(f"\n📁 项目目录: {project_dir}")
    print(f"📦 虚拟环境: {'✅ 存在' if status['venv_exists'] else '❌ 不存在'}")
    
    if status["venv_exists"]:
        print(f"🐍 Python: {status['python_path']}")
        print(f"📚 RapidOCR: {'✅ 已安装' if status['rapidocr_installed'] else '❌ 未安装'}")
    
    if args.check:
        if status["venv_exists"] and status["rapidocr_installed"]:
            print("\n✅ 环境已就绪！")
            print("\n📋 MCP 配置:")
            print(json.dumps(get_mcp_config(project_dir), indent=2, ensure_ascii=False))
        else:
            print("\n⚠️  需要安装依赖")
            print(f"\n💡 运行: python3 setup.py --mirror tsinghua")
        return
    
    # 安装模式
    if not status["venv_exists"] or not status["rapidocr_installed"]:
        print("\n📥 安装依赖...")
        setup_cmd = [sys.executable, str(project_dir / "setup.py")]
        if args.mirror:
            setup_cmd.extend(["--mirror", args.mirror])
        
        result = subprocess.run(setup_cmd, cwd=str(project_dir))
        
        if result.returncode != 0:
            print("\n❌ 安装失败")
            sys.exit(1)
        
        # 重新检查状态
        status = check_environment(project_dir)
    
    if status["venv_exists"] and status["rapidocr_installed"]:
        print("\n" + "=" * 50)
        print("🎉 安装完成！")
        print("=" * 50)
        print("\n📋 MCP 配置（请将以下配置添加到你的 AI 工具中）:")
        print(json.dumps(get_mcp_config(project_dir), indent=2, ensure_ascii=False))
    else:
        print("\n⚠️  安装可能不完整，请检查上方输出")


if __name__ == "__main__":
    main()
