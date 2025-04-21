#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证中间件
Created by: tao-xiaoxin
Created time: 2025-02-19 11:16:02
"""
import re
from typing import Any, Coroutine

from fastapi import Request, Response, HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError
from starlette.requests import HTTPConnection

from core.conf import settings
from engines import mysql_manager, AsyncDBSession
from utils.token_manager import token_manager as token
from utils.exception import TokenError
from utils.log import log
from utils.responses import APIResponse

# 废弃的直接获取get_db方式,保留向后兼容性
get_db = mysql_manager.get_db


class _AuthenticationError(AuthenticationError):
    """自定义认证错误"""

    def __init__(
            self,
            code: int = 401,
            message: str = "Authentication failed",
            headers: dict[str, Any] | None = None
    ):
        self.code = code
        self.message = message
        self.headers = headers or {}


class TokenUser:
    """令牌用户类"""

    def __init__(self, user_id: str, token_data: dict):
        self.user_id = user_id
        self.token_data = token_data
        self.is_authenticated = True

    @property
    def identity(self) -> str:
        return self.user_id

    @property
    def display_name(self) -> str:
        return self.token_data.get("username", self.user_id)


class AuthMiddleware(AuthenticationBackend):
    """认证中间件"""

    @staticmethod
    def auth_exception_handler(conn: HTTPConnection, exc: _AuthenticationError) -> Response:
        """
        认证异常处理器

        Args:
            conn: HTTP连接对象
            exc: 认证异常

        Returns:
            Response: JSON响应
        """
        return APIResponse.error(
            code=exc.code,
            msg=exc.message,
            headers=exc.headers
        )

    async def authenticate(self, request: Request) -> tuple[AuthCredentials, TokenUser] | None:
        """
        认证处理

        Args:
            request: 请求对象

        Returns:
            tuple[AuthCredentials, TokenUser] | None: 认证凭证和用户对象或None

        Raises:
            _AuthenticationError: 认证失败时抛出
        """
        # 1. 检查是否为免认证路径
        path = request.url.path

        # 检查路径是否匹配白名单中的任何模式（包括正则表达式模式）
        for pattern in settings.AUTH_EXCLUDE_PATHS:
            if pattern == path:  # 直接匹配
                return None
            elif pattern.find('[') >= 0:  # 如果包含 '[', 可能是正则表达式
                try:
                    if re.match(f"^{pattern}$", path):
                        return None
                except re.error:
                    continue  # 如果正则表达式无效，继续检查下一个

        # 2. 对于非免认证路径，必须提供认证头
        auth_header = request.headers.get("Authorization")
        token_type = request.headers.get("X-Token-Type", "access")  # 默认为访问令牌
        if not auth_header:
            raise _AuthenticationError(
                code=401,
                message="Authentication required"
            )

        # 3. 验证认证方案
        scheme, credentials = get_authorization_scheme_param(auth_header)
        if scheme.lower() != settings.TOKEN_TYPE.lower():
            raise _AuthenticationError(
                code=401,
                message="Invalid authentication scheme"
            )

        try:
            # 4. 验证令牌
            token_data = await token.verify_token(credentials, token_type=token_type)
            if not token_data:
                raise _AuthenticationError(
                    code=401,
                    message="Invalid token"
                )

            # 5. 获取用户ID
            user_id = token_data.get("sub")
            if not user_id:
                raise _AuthenticationError(
                    code=401,
                    message="Invalid token payload"
                )

            # 6. 创建用户对象
            user = TokenUser(
                user_id=user_id,
                token_data=token_data
            )

            return AuthCredentials(["authenticated"]), user
        except TokenError as e:
            raise _AuthenticationError(
                code=e.code,
                message=e.detail,
                headers=e.headers
            )
        except HTTPException as e:
            raise _AuthenticationError(
                message=e.detail,
                headers=e.headers
            )
        except Exception as e:
            # 处理其他未预期的异常
            log.error(f"Authentication failed: {str(e)}")
            raise _AuthenticationError(
                code=getattr(e, "code", 500),
                message=getattr(e, "message", e)
            )

# 注意：AccessKey验证相关代码已被移除
# 令牌验证现在完全通过Redis实现
# 这种设计提供了更好的性能和水平扩展能力
