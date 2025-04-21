#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from utils.log import log
from utils.timezone import timezone


class AccessMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 创建带有请求上下文的日志记录器
        request_logger = log.with_request(request)
        
        # 记录请求开始
        start_time = timezone.now
        request_logger.info(f"开始处理请求 {request.method} {request.url.path}")
        
        # 处理请求
        try:
            response = await call_next(request)
            end_time = timezone.now
            process_time = round((end_time - start_time).total_seconds(), 3) * 1000.0
            
            # 根据状态码选择日志级别
            if response.status_code >= 500:
                log_method = request_logger.error
            elif response.status_code >= 400:
                log_method = request_logger.warning
            else:
                log_method = request_logger.success
                
            # 记录完整请求信息
            log_method(
                f"请求完成",
                status=response.status_code,
                time=f"{process_time}ms",
                path=request.url.path,
            )
            
            return response
        except Exception as e:
            # 记录异常信息
            end_time = timezone.now
            process_time = round((end_time - start_time).total_seconds(), 3) * 1000.0
            request_logger.error(
                f"请求处理异常: {str(e)}",
                exc_info=True,
                time=f"{process_time}ms",
                path=request.url.path,
            )
            raise
