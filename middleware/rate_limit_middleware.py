#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
速率限制中间件 - 防止API滥用
"""
import time
from typing import Dict, Optional, Callable, Awaitable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from engines.redis import redis_client
from utils.log import log


class RateLimitMiddleware(BaseHTTPMiddleware):
    """请求频率限制中间件"""
    
    def __init__(
        self, 
        app: ASGIApp, 
        limit: int = 60,
        window: int = 60,
        exempt_paths: Optional[list] = None,
        get_identifier: Optional[Callable[[Request], str]] = None,
        redis_db: Optional[int] = None
    ):
        """
        初始化速率限制中间件
        
        Args:
            app: ASGI应用
            limit: 在时间窗口内允许的最大请求数
            window: 时间窗口大小（秒）
            exempt_paths: 豁免的路径列表（不受限制）
            get_identifier: 自定义函数，用于从请求获取唯一标识符
            redis_db: Redis数据库索引，用于存储速率限制计数器
        """
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.exempt_paths = exempt_paths or []
        self.get_identifier = get_identifier or self._default_identifier
        self.redis_db = redis_db
    
    @staticmethod
    def _default_identifier(request: Request) -> str:
        """
        获取请求的默认唯一标识符（IP地址）
        
        Args:
            request: 请求对象
            
        Returns:
            str: 请求的唯一标识符
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        调度请求处理
        
        Args:
            request: 请求对象
            call_next: 下一个请求处理器
            
        Returns:
            Response: 响应对象
        """
        # 检查是否为豁免路径
        path = request.url.path
        if any(path.startswith(exempt) for exempt in self.exempt_paths):
            return await call_next(request)
        
        # 获取请求标识符
        identifier = self.get_identifier(request)
        
        # 构建Redis键
        current_time = int(time.time())
        time_window = current_time // self.window
        rate_limit_key = f"ratelimit:{identifier}:{time_window}"
        
        # 获取当前计数并递增
        current_count = redis_client.get(rate_limit_key, db=self.redis_db)
        
        if current_count is None:
            # 如果键不存在，设置初始值为1，并设置过期时间
            current_count = 1
            redis_client.set(rate_limit_key, 1, self.window, db=self.redis_db)
        else:
            try:
                current_count = int(current_count) + 1
                redis_client.set(rate_limit_key, current_count, self.window, db=self.redis_db)
            except (ValueError, TypeError):
                log.error(f"Invalid rate limit counter value: {current_count}")
                current_count = 1
                redis_client.set(rate_limit_key, 1, self.window, db=self.redis_db)
        
        # 添加速率限制头
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(max(0, self.limit - current_count)),
            "X-RateLimit-Reset": str(time_window * self.window + self.window)
        }
        
        # 检查是否超过限制
        if current_count > self.limit:
            log.warning(f"Rate limit exceeded for {identifier}: {current_count}/{self.limit}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers=headers
            )
        
        # 处理请求
        response = await call_next(request)
        
        # 添加速率限制头到响应
        for name, value in headers.items():
            response.headers[name] = value
        
        return response


def setup_rate_limit_middleware(
    app: FastAPI, 
    limit: int = 60, 
    window: int = 60,
    exempt_paths: Optional[list] = None,
    redis_db: Optional[int] = None
) -> None:
    """
    设置速率限制中间件
    
    Args:
        app: FastAPI应用实例
        limit: 在时间窗口内允许的最大请求数
        window: 时间窗口大小（秒）
        exempt_paths: 豁免的路径列表（例如：["/docs", "/redoc"]）
        redis_db: Redis数据库索引，用于存储速率限制计数器
    """
    app.add_middleware(
        RateLimitMiddleware,
        limit=limit,
        window=window,
        exempt_paths=exempt_paths or ["/docs", "/redoc", "/openapi.json"],
        redis_db=redis_db
    ) 