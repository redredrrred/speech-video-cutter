#!/usr/bin/env python3
"""
AI智能口误去除工具 - 主程序入口
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.cli import main

if __name__ == '__main__':
    main()
