#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局异常处理模块
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Union, Dict, Any

from utils.log import log


def register_exception(app: FastAPI) -> None:
    """
    注册全局异常处理器
    
    Args:
        app: FastAPI应用实例
    """
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        """
        处理Pydantic验证错误
        """
        log.error(f"Validation error: {exc}")
        return JSONResponse(
            status_code=422,
            content={
                "code": 422,
                "message": "数据验证错误",
                "detail": exc.errors()
            }
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        处理所有未捕获的异常
        """
        log.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "服务器内部错误",
                "detail": str(exc)
            }
        )
    
    log.info("Global exception handlers registered")


class NotFoundException(Exception):
    """资源不存在异常"""
    def __init__(self, detail: str):
        self.detail = detail


class AuthenticationException(Exception):
    """认证失败异常"""
    def __init__(self, detail: str):
        self.detail = detail


class ForbiddenException(Exception):
    """权限不足异常"""
    def __init__(self, detail: str):
        self.detail = detail 