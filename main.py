#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPIX 入口文件
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from core.registrar import register_app

# 注册应用
app = register_app()

if __name__ == "__main__":
    import uvicorn
    from core.conf import settings
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
