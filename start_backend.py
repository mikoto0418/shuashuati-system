#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
刷刷题系统后端启动脚本

这个脚本用于启动Flask后端服务，包含以下功能：
1. 环境检查
2. 依赖检查
3. 数据库初始化
4. 启动Flask应用
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("❌ 错误：需要Python 3.7或更高版本")
        print(f"当前版本：{sys.version}")
        return False
    print(f"✅ Python版本检查通过：{sys.version.split()[0]}")
    return True

def check_dependencies():
    """检查依赖包"""
    try:
        import flask
        import flask_sqlalchemy
        import flask_cors
        print("✅ 核心依赖包检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包：{e}")
        print("请运行：pip install -r backend/requirements.txt")
        return False

def setup_environment():
    """设置环境变量"""
    # 切换到backend目录
    backend_dir = Path(__file__).parent / 'backend'
    if backend_dir.exists():
        os.chdir(backend_dir)
        print(f"✅ 切换到后端目录：{backend_dir.absolute()}")
    else:
        print("❌ 找不到backend目录")
        return False
    
    # 设置Python路径
    if str(backend_dir.absolute()) not in sys.path:
        sys.path.insert(0, str(backend_dir.absolute()))
    
    return True

def start_flask_app():
    """启动Flask应用"""
    try:
        print("🚀 启动刷刷题系统后端服务...")
        print("📍 服务地址：http://localhost:5000")
        print("📍 健康检查：http://localhost:5000/api/health")
        print("📍 按 Ctrl+C 停止服务")
        print("-" * 50)
        
        # 导入并运行Flask应用
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败：{e}")
        return False
    
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("🎯 刷刷题系统后端启动器")
    print("=" * 50)
    
    # 环境检查
    if not check_python_version():
        sys.exit(1)
    
    if not setup_environment():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # 启动应用
    start_flask_app()

if __name__ == '__main__':
    main()