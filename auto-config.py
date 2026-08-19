#!/usr/bin/env python3
"""一键配置脚本 - 让 AI 自动完成 MCP 配置

使用方法:
    python auto-config.py                    # 自动配置 VS Code
    python auto-config.py --client claude    # 配置 Claude Desktop
    python auto-config.py --client cursor    # 配置 Cursor
    python auto-config.py --output           # 仅输出配置内容
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


def get_vscode_settings_path() -> Path | None:
    """获取 VS Code 设置文件路径"""
    if platform.system() == "Darwin":
        return Path.home() / "Library/Application Support/Code/User/settings.json"
    elif platform.system() == "Windows":
        return Path(os.environ.get("APPDATA", "")) / "Code/User/settings.json"
    else:
        return Path.home() / ".config/Code/User/settings.json"


def get_claude_config_path() -> Path | None:
    """获取 Claude Desktop 配置文件路径"""
    if platform.system() == "Darwin":
        return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    elif platform.system() == "Windows":
        return Path(os.environ.get("APPDATA", "")) / "Claude/claude_desktop_config.json"
    return None


def get_cursor_config_path(project_dir: Path) -> Path:
    """获取 Cursor 配置文件路径"""
    return project_dir / ".cursor/mcp.json"


def update_vscode_config(config: dict) -> bool:
    """更新 VS Code 配置"""
    settings_path = get_vscode_settings_path()
    if not settings_path or not settings_path.exists():
        print(f"❌ VS Code 设置文件不存在: {settings_path}")
        return False
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    except Exception as e:
        print(f"❌ 读取设置文件失败: {e}")
        return False
    
    # 更新 MCP 配置
    if "github.copilot.chat.mcp.servers" not in settings:
        settings["github.copilot.chat.mcp.servers"] = {}
    
    settings["github.copilot.chat.mcp.servers"].update(config["mcpServers"])
    
    try:
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        print(f"✅ VS Code 配置已更新: {settings_path}")
        return True
    except Exception as e:
        print(f"❌ 写入设置文件失败: {e}")
        return False


def update_claude_config(config: dict) -> bool:
    """更新 Claude Desktop 配置"""
    config_path = get_claude_config_path()
    if not config_path:
        print("❌ 不支持的操作系统")
        return False
    
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                claude_config = json.load(f)
        else:
            claude_config = {}
            config_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return False
    
    if "mcpServers" not in claude_config:
        claude_config["mcpServers"] = {}
    
    claude_config["mcpServers"].update(config["mcpServers"])
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(claude_config, f, indent=2, ensure_ascii=False)
        print(f"✅ Claude Desktop 配置已更新: {config_path}")
        return True
    except Exception as e:
        print(f"❌ 写入配置文件失败: {e}")
        return False


def update_cursor_config(config: dict, project_dir: Path) -> bool:
    """更新 Cursor 配置"""
    config_path = get_cursor_config_path(project_dir)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ Cursor 配置已创建: {config_path}")
        return True
    except Exception as e:
        print(f"❌ 写入配置文件失败: {e}")
        return False


def check_installation(project_dir: Path) -> bool:
    """检查是否已安装"""
    venv_dir = project_dir / ".venv"
    if not venv_dir.exists():
        print("⚠️  虚拟环境不存在，请先运行: python3 setup.py --mirror tsinghua")
        return False
    
    python_path = get_venv_python(project_dir)
    if not Path(python_path).exists():
        print("⚠️  Python 不存在，请先运行: python3 setup.py --mirror tsinghua")
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(description="一键配置 MCP")
    parser.add_argument("--client", "-c", 
                       choices=["vscode", "claude", "cursor", "all"],
                       default="vscode",
                       help="配置哪个客户端 (默认: vscode)")
    parser.add_argument("--output", "-o", action="store_true",
                       help="仅输出配置内容，不写入文件")
    parser.add_argument("--force", "-f", action="store_true",
                       help="强制配置，跳过检查")
    args = parser.parse_args()
    
    project_dir = get_project_dir()
    
    print("=" * 50)
    print("🔧 CH OCR MCP Pro 自动配置")
    print("=" * 50)
    
    # 检查安装
    if not args.force and not check_installation(project_dir):
        print("\n💡 请先运行安装脚本:")
        print("   python3 setup.py --mirror tsinghua")
        sys.exit(1)
    
    # 生成配置
    config = get_mcp_config(project_dir)
    
    if args.output:
        print("\n📋 MCP 配置:")
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return
    
    print(f"\n📦 项目目录: {project_dir}")
    print(f"🐍 Python: {get_venv_python(project_dir)}")
    
    success = True
    
    if args.client in ["vscode", "all"]:
        print("\n🔧 配置 VS Code...")
        if not update_vscode_config(config):
            success = False
    
    if args.client in ["claude", "all"]:
        print("\n🔧 配置 Claude Desktop...")
        if not update_claude_config(config):
            success = False
    
    if args.client in ["cursor", "all"]:
        print("\n🔧 配置 Cursor...")
        if not update_cursor_config(config, project_dir):
            success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 配置完成！")
        print("\n💡 请重启你的 AI 工具以使配置生效")
    else:
        print("⚠️  配置过程中有错误，请检查上方输出")
    print("=" * 50)


if __name__ == "__main__":
    main()
