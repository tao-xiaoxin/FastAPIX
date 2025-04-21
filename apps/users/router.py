from fastapi import APIRouter, Depends, HTTPException
from typing import List
from apps.users.schemas import UserCreate, UserRead, UserUpdate
from apps.users.service import UserService
from core.dependencies import get_user_repository
from utils.response import APIResponse

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.post("/")
async def create_user(user: UserCreate, user_service: UserService = Depends(lambda: UserService(get_user_repository()))):
    created_user = user_service.create_user(user)
    return APIResponse.success(data=created_user, msg="用户创建成功")

@users_router.get("/{user_id}")
async def get_user(user_id: int, user_service: UserService = Depends(lambda: UserService(get_user_repository()))):
    user = user_service.get_user(user_id)
    if not user:
        return APIResponse.error(msg="用户不存在", code=404, status_code=404)
    return APIResponse.detail(data=user, msg="获取用户成功")

@users_router.get("/")
async def list_users(skip: int = 0, limit: int = 10, user_service: UserService = Depends(lambda: UserService(get_user_repository()))):
    users = user_service.get_users(skip, limit)
    return APIResponse.success(data=users, msg="获取用户列表成功", page=skip//limit+1, limit=limit, total=len(users))

@users_router.put("/{user_id}")
async def update_user(user_id: int, user: UserUpdate, user_service: UserService = Depends(lambda: UserService(get_user_repository()))):
    updated_user = user_service.update_user(user_id, user)
    if not updated_user:
        return APIResponse.error(msg="用户不存在", code=404, status_code=404)
    return APIResponse.success(data=updated_user, msg="用户更新成功")

@users_router.delete("/{user_id}")
async def delete_user(user_id: int, user_service: UserService = Depends(lambda: UserService(get_user_repository()))):
    deleted = user_service.delete_user(user_id)
    if not deleted:
        return APIResponse.error(msg="用户不存在", code=404, status_code=404)
    return APIResponse.success(data=None, msg="用户删除成功")