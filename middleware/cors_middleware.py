#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORS中间件 - 处理跨域资源共享
"""
from typing import List, Optional, Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings


def setup_cors_middleware(app: FastAPI) -> None:
    """
    设置CORS中间件
    
    Args:
        app: FastAPI应用实例
    """
    # 获取允许的源列表
    # 如果设置了BACKEND_CORS_ORIGINS，则使用该设置
    # 否则允许所有源（['*']）
    origins = settings.BACKEND_CORS_ORIGINS or ['*']
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],  # 允许所有HTTP方法
        allow_headers=["*"],  # 允许所有HTTP头
    ) 