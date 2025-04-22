#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用注册器
Created by: tao-xiaoxin
Created time: 2025-02-18 10:59:29
"""

import os
from fastapi import FastAPI
from core.conf import settings
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from engines import mysql_manager, redis_client
from core.path_conf import STATIC_DIR
from starlette.middleware.authentication import AuthenticationMiddleware
from middleware.access_middleware import AccessMiddleware
from middleware.auth_middleware import AuthMiddleware
from utils.exception import register_exception
from utils.response import APIResponse
from core.router import routers as main_router


@asynccontextmanager
async def register_init(app: FastAPI):
    """
    启动初始化处理器

    在应用启动时初始化必要的服务，在应用关闭时清理资源

    Args:
        app: FastAPI 应用实例
    """
    # 初始化数据库连接
    await mysql_manager.init_database()

    # 连接 redis
    await redis_client.open()

    yield  # 应用运行时

    # 关闭数据库连接
    # await mysql_manager.close_database()

    # 关闭 redis 连接
    await redis_client.close()


def register_app():
    """
    注册应用

    初始化 FastAPI 应用并配置所有必要的组件

    Returns:
        FastAPI: 配置完成的 FastAPI 应用实例
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOCS_URL,
        openapi_url=settings.OPENAPI_URL,
        default_response_class=APIResponse,
        lifespan=register_init  # 使用异步上下文管理器管理应用生命周期
    )

    # 注册静态文件
    register_static_file(app)

    # 注册中间件
    register_middleware(app)

    # 注册路由
    register_router(app)

    # 注册全局异常处理
    register_exception(app)

    return app


def register_static_file(app: FastAPI):
    """
    静态文件交互开发模式, 生产使用 nginx 静态资源服务

    :param app:
    :return:
    """
    # 检查是否应该挂载静态文件，默认为True
    if getattr(settings, "STATIC_FILES", True):
        if not os.path.exists(STATIC_DIR):
            os.mkdir(STATIC_DIR)
        app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')
        
    # 检查是否有MEDIA_ROOT设置
    media_root = getattr(settings, "MEDIA_ROOT", None)
    if media_root:
        # 确保目录存在
        if not os.path.exists(media_root):
            os.makedirs(media_root, exist_ok=True)
        app.mount("/media", StaticFiles(directory=media_root), name="media")


def register_middleware(app: FastAPI):
    """
    注册中间件
    中间件的执行顺序与注册顺序相反：最后注册的最先执行
    
    Args:
        app: FastAPI应用实例
    """
    # 1. CORS中间件（最先注册，处理HTTP头）
    if settings.MIDDLEWARE_CORS:
        from middleware.cors_middleware import setup_cors_middleware
        setup_cors_middleware(app)

    # 2. 速率限制中间件
    if getattr(settings, "MIDDLEWARE_RATE_LIMIT", False):
        from middleware.rate_limit_middleware import setup_rate_limit_middleware
        setup_rate_limit_middleware(
            app,
            limit=getattr(settings, "RATE_LIMIT_REQUESTS", 60),
            window=getattr(settings, "RATE_LIMIT_WINDOW", 60),
            redis_db=getattr(settings, "RATE_LIMIT_REDIS_DB", None)
        )

    # 3. 认证中间件
    app.add_middleware(
        AuthenticationMiddleware,
        backend=AuthMiddleware(),
        on_error=AuthMiddleware.auth_exception_handler
    )

    # 4. 访问日志中间件
    if settings.MIDDLEWARE_ACCESS:
        app.add_middleware(AccessMiddleware)


def register_router(app: FastAPI):
    """
    路由

    :param app: FastAPI
    :return:
    """

    app.include_router(main_router)
