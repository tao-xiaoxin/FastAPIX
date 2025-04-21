from typing import List, Optional
from fastapi import Depends, HTTPException
from apps.users.schemas import UserCreate, UserRead, UserUpdate
from apps.users.service import UserService
from core.dependencies import get_user_service
from utils.response import APIResponse

async def create_user(
    user: UserCreate, 
    user_service: UserService = Depends(get_user_service)
):
    """创建新用户"""
    created_user = user_service.create_user(user)
    return APIResponse.success(data=created_user, msg="用户创建成功")


async def get_user(
    user_id: int, 
    user_service: UserService = Depends(get_user_service)
):
    """获取指定ID的用户"""
    user = user_service.get_user(user_id)
    if not user:
        return APIResponse.error(msg="用户不存在", code=404, status_code=404)
    return APIResponse.detail(data=user, msg="获取用户成功")


async def list_users(
    skip: int = 0, 
    limit: int = 10, 
    user_service: UserService = Depends(get_user_service)
):
    """获取用户列表"""
    users = user_service.get_users(skip, limit)
    return APIResponse.success(data=users, msg="获取用户列表成功", page=skip//limit+1, limit=limit, total=len(users))


async def update_user(
    user_id: int, 
    user: UserUpdate, 
    user_service: UserService = Depends(get_user_service)
):
    """更新用户信息"""
    updated_user = user_service.update_user(user_id, user)
    if not updated_user:
        return APIResponse.error(msg="用户不存在", code=404, status_code=404)
    return APIResponse.success(data=updated_user, msg="用户更新成功")


async def delete_user(
    user_id: int, 
    user_service: UserService = Depends(get_user_service)
):
    """删除用户"""
    deleted = user_service.delete_user(user_id)
    if not deleted:
        return APIResponse.error(msg="用户不存在", code=404, status_code=404)
    return APIResponse.success(data=None, msg="用户删除成功") 