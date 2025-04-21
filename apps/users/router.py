from fastapi import APIRouter
from apps.users.handlers import UserHandler
from core.dependencies import get_user_handler

users_router = APIRouter(prefix="/users", tags=["users"])

# 从handlers导入处理函数
from apps.users.handlers import (
    create_user,
    get_user,
    list_users,
    update_user,
    delete_user
)

# 用户管理路由
users_router.add_api_route(
    path="/",
    endpoint=create_user,
    methods=["POST"],
    description="创建用户",
)

users_router.add_api_route(
    path="/{user_id}",
    endpoint=get_user,
    methods=["GET"],
    description="获取用户详情",
)

users_router.add_api_route(
    path="/",
    endpoint=list_users,
    methods=["GET"],
    description="获取用户列表",
)

users_router.add_api_route(
    path="/{user_id}",
    endpoint=update_user,
    methods=["PUT"],
    description="更新用户信息",
)

users_router.add_api_route(
    path="/{user_id}",
    endpoint=delete_user,
    methods=["DELETE"],
    description="删除用户",
)