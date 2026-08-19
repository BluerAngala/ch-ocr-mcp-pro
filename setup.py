#!/usr/bin/env python3
"""自动安装脚本 - 支持国内镜像加速

使用方法:
    python setup.py              # 默认安装
    python setup.py --mirror     # 使用清华镜像加速
    python setup.py --check      # 仅检查环境
"""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

# 国内镜像源
MIRRORS = {
    "tsinghua": "https://pypi.tuna.tsinghua.edu.cn/simple/",
    "aliyun": "https://mirrors.aliyun.com/pypi/simple/",
    "ustc": "https://pypi.mirrors.ustc.edu.cn/simple/",
    "huawei": "https://repo.huaweicloud.com/repository/pypi/simple/",
}

# 依赖列表
DEPENDENCIES = [
    "mcp>=1.27",
    "rapidocr-onnxruntime>=1.2",
    "onnxruntime>=1.20",
    "pytesseract>=0.3.13",
    "Pillow>=10",
    "numpy>=1.24",
    "pymupdf>=1.24",
    "jiwer>=3",
    "opencv-python-headless>=4.8",
    "pyperclip>=1.8",
]


def get_system_info() -> dict:
    """获取系统信息"""
    return {
        "platform": platform.system(),
        "arch": platform.machine(),
        "python": sys.executable,
        "python_version": platform.python_version(),
        "is_arm": platform.machine() in ("arm64", "aarch64"),
    }


def check_python() -> bool:
    """检查 Python 版本"""
    if sys.version_info < (3, 12):
        print(f"❌ Python 版本过低: {sys.version}")
        print("   需要 Python 3.12+，推荐 3.12")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_venv() -> tuple[bool, Path]:
    """检查是否在虚拟环境中"""
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    venv_path = Path(sys.prefix) if in_venv else None
    return in_venv, venv_path


def create_venv(project_dir: Path) -> Path:
    """创建虚拟环境"""
    venv_dir = project_dir / ".venv"
    if venv_dir.exists():
        print(f"✅ 虚拟环境已存在: {venv_dir}")
        return venv_dir

    print(f"📦 创建虚拟环境: {venv_dir}")
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    print("✅ 虚拟环境创建成功")
    return venv_dir


def get_pip_cmd(venv_dir: Path | None) -> list[str]:
    """获取 pip 命令"""
    if venv_dir:
        if platform.system() == "Windows":
            return [str(venv_dir / "Scripts" / "pip.exe")]
        return [str(venv_dir / "bin" / "pip")]
    return [sys.executable, "-m", "pip"]


def install_dependencies(
    pip_cmd: list[str],
    mirror: str | None = None,
    upgrade: bool = False,
) -> bool:
    """安装依赖"""
    cmd = pip_cmd + ["install"]
    if upgrade:
        cmd.append("--upgrade")
    if mirror:
        mirror_url = MIRRORS.get(mirror, mirror)
        cmd.extend(["-i", mirror_url, "--trusted-host", mirror_url.split("//")[1].split("/")[0]])
        print(f"🚀 使用镜像: {mirror_url}")
    cmd.extend(DEPENDENCIES)

    print("📥 安装依赖中...")
    print(f"   命令: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ 依赖安装成功")
            return True
        else:
            print(f"❌ 安装失败:\n{result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ 安装超时（5分钟）")
        return False


def verify_installation(pip_cmd: list[str]) -> dict:
    """验证安装"""
    results = {}
    packages = [
        ("rapidocr_onnxruntime", "RapidOCR"),
        ("onnxruntime", "ONNX Runtime"),
        ("PIL", "Pillow"),
        ("numpy", "NumPy"),
        ("fitz", "PyMuPDF"),
        ("jiwer", "jiwer"),
        ("cv2", "OpenCV"),
    ]

    # 获取 Python 解释器路径（从 pip 命令推断）
    python_cmd = sys.executable
    if pip_cmd and len(pip_cmd) > 0:
        pip_path = pip_cmd[0]
        if "bin/pip" in pip_path:
            python_cmd = pip_path.replace("bin/pip", "bin/python")
        elif "Scripts/pip" in pip_path:
            python_cmd = pip_path.replace("Scripts/pip", "Scripts/python")
        elif "pip" in pip_path and "python" not in pip_path:
            # pip 在 PATH 中，使用当前 Python
            python_cmd = sys.executable

    # 确保 Python 路径存在
    if not Path(python_cmd).exists():
        python_cmd = sys.executable

    for module, name in packages:
        try:
            # 使用 subprocess 检查，避免当前进程的模块缓存
            result = subprocess.run(
                [python_cmd, "-c", f"import {module}; print('ok')"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            results[name] = "✅" if result.returncode == 0 else "❌"
        except Exception as e:
            results[name] = f"❌"

    # 检查 Tesseract（可选）
    import shutil
    if shutil.which("tesseract"):
        results["Tesseract"] = "✅ (可选)"
    else:
        results["Tesseract"] = "⚠️ 未安装（可选）"

    return results


def generate_launcher(project_dir: Path, venv_dir: Path) -> None:
    """生成启动脚本"""
    src_dir = project_dir / "src"
    # Windows
    bat_content = f"""@echo off
set PYTHONPATH={src_dir}
"{venv_dir / 'Scripts' / 'python.exe'}" -m ocr_mcp %*
"""
    bat_path = project_dir / "run.bat"
    bat_path.write_text(bat_content, encoding="utf-8")

    # Unix
    sh_content = f"""#!/bin/bash
PYTHONPATH="{src_dir}" "{venv_dir / 'bin' / 'python'}" -m ocr_mcp "$@"
"""
    sh_path = project_dir / "run.sh"
    sh_path.write_text(sh_content, encoding="utf-8")
    os.chmod(sh_path, 0o755)

    print(f"✅ 启动脚本已生成: {bat_path} / {sh_path}")


def generate_mcp_config(project_dir: Path, venv_dir: Path) -> None:
    """生成 MCP 配置示例"""
    python_path = venv_dir / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")
    src_dir = project_dir / "src"

    config = {
        "mcpServers": {
            "ocr": {
                "command": str(python_path),
                "args": ["-m", "ocr_mcp"],
                "env": {
                    "PYTHONUTF8": "1",
                    "PYTHONUNBUFFERED": "1",
                    "PYTHONPATH": str(src_dir),
                }
            }
        }
    }

    config_path = project_dir / "mcp_config.example.json"
    import json
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ MCP 配置示例已生成: {config_path}")


def main():
    parser = argparse.ArgumentParser(description="OCR MCP 自动安装脚本")
    parser.add_argument("--mirror", "-m", nargs="?", const="tsinghua",
                       help="使用国内镜像 (tsinghua/aliyun/ustc/huawei)")
    parser.add_argument("--check", "-c", action="store_true", help="仅检查环境")
    parser.add_argument("--upgrade", "-u", action="store_true", help="升级依赖")
    parser.add_argument("--no-venv", action="store_true", help="不创建虚拟环境（直接安装到当前环境）")
    args = parser.parse_args()

    project_dir = Path(__file__).parent.resolve()
    print("=" * 60)
    print("🚀 OCR MCP 自动安装脚本")
    print("=" * 60)

    # 系统信息
    info = get_system_info()
    print(f"\n📋 系统信息:")
    print(f"   平台: {info['platform']} {info['arch']}")
    print(f"   Python: {info['python_version']}")
    print(f"   路径: {info['python']}")

    # 检查 Python
    print(f"\n🔍 检查 Python 版本...")
    if not check_python():
        sys.exit(1)

    # 检查虚拟环境
    in_venv, venv_path = check_venv()
    if in_venv:
        print(f"✅ 已在虚拟环境中: {venv_path}")

    if args.check:
        print("\n📦 检查依赖安装状态...")
        # 如果存在虚拟环境，使用虚拟环境的 pip
        venv_dir = project_dir / ".venv"
        if venv_dir.exists():
            pip_cmd = get_pip_cmd(venv_dir)
            print(f"   使用虚拟环境: {venv_dir}")
        else:
            pip_cmd = [sys.executable, "-m", "pip"]
        results = verify_installation(pip_cmd)
        for name, status in results.items():
            print(f"   {status} {name}")
        return

    # 创建虚拟环境
    venv_dir = None
    if not args.no_venv and not in_venv:
        print(f"\n📦 创建虚拟环境...")
        venv_dir = create_venv(project_dir)
        pip_cmd = get_pip_cmd(venv_dir)
    else:
        pip_cmd = get_pip_cmd(None)

    # 安装依赖
    print(f"\n📥 安装依赖...")
    mirror = args.mirror or os.environ.get("PIP_MIRROR")
    if not mirror and os.environ.get("USE_CHINA_MIRROR", "").lower() in ("1", "true", "yes"):
        mirror = "tsinghua"

    success = install_dependencies(pip_cmd, mirror=mirror, upgrade=args.upgrade)
    if not success:
        print("\n💡 提示: 如果安装慢，试试国内镜像:")
        print("   python setup.py --mirror tsinghua")
        print("   python setup.py --mirror aliyun")
        sys.exit(1)

    # 安装项目本身（editable mode）
    print(f"\n📦 安装项目...")
    try:
        install_cmd = pip_cmd + ["install", "-e", ".", "--no-deps"]
        if mirror:
            mirror_url = MIRRORS.get(mirror, mirror)
            install_cmd.extend(["-i", mirror_url])
            host = mirror_url.split("//")[1].split("/")[0]
            install_cmd.extend(["--trusted-host", host])
        subprocess.run(install_cmd, capture_output=True, text=True, timeout=60, cwd=str(project_dir))
        print("✅ 项目安装成功")
    except Exception as e:
        print(f"⚠️  项目安装警告: {e}")

    # 验证安装
    print(f"\n🔍 验证安装...")
    results = verify_installation(pip_cmd)
    all_ok = all("✅" in v for k, v in results.items() if k != "Tesseract")
    for name, status in results.items():
        print(f"   {status} {name}")

    # 生成启动脚本和配置
    if venv_dir:
        generate_launcher(project_dir, venv_dir)
        generate_mcp_config(project_dir, venv_dir)

    print("\n" + "=" * 60)
    if all_ok:
        print("🎉 安装完成！")
        print("\n📝 使用方法:")
        print(f"   1. 运行服务器: python -m ocr_mcp")
        if venv_dir:
            print(f"   2. 或使用启动脚本: ./run.sh")
        print(f"   3. 查看 MCP 配置: {project_dir / 'mcp_config.example.json'}")
        print(f"\n💡 将 MCP 配置添加到你的 AI 工具中即可使用！")
    else:
        print("⚠️ 安装完成，但部分依赖可能有问题")
    print("=" * 60)


if __name__ == "__main__":
    main()
