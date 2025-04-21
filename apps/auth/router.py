from fastapi import APIRouter, Depends
from apps.auth.handlers import AuthHandler
from core.dependencies import get_auth_handler

# 创建认证路由器
auth_router = APIRouter(prefix="/auth", tags=["auth"])

# 从handlers导入处理函数
from apps.auth.handlers import (
    login,
    register,
    create_access_key,
    list_access_keys,
    issue_token,
    refresh_token,
    revoke_token,
)

# 用户认证路由
auth_router.add_api_route(
    path="/login",
    endpoint=login,
    methods=["POST"],
    description="用户登录",
)

auth_router.add_api_route(
    path="/register",
    endpoint=register,
    methods=["POST"],
    description="用户注册",
)

# 访问密钥管理路由
auth_router.add_api_route(
    path="/keys",
    endpoint=create_access_key,
    methods=["POST"],
    description="创建访问密钥",
)

auth_router.add_api_route(
    path="/keys",
    endpoint=list_access_keys,
    methods=["GET"],
    description="获取访问密钥列表",
)

# Token管理路由
auth_router.add_api_route(
    path="/token",
    endpoint=issue_token,
    methods=["POST"],
    description="签发访问令牌",
)

auth_router.add_api_route(
    path="/token/refresh",
    endpoint=refresh_token,
    methods=["POST"],
    description="刷新访问令牌",
)

auth_router.add_api_route(
    path="/token/revoke",
    endpoint=revoke_token,
    methods=["POST"],
    description="撤销访问令牌",
)