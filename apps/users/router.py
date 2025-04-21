from fastapi import APIRouter, Depends, HTTPException
from typing import List
from apps.users.schemas import UserCreate, UserRead, UserUpdate
from apps.users.service import UserService
from core.dependencies import get_user_repository

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, user_service: UserService = Depends(lambda: UserService(get_user_repository()))):
    return user_service.create_user(user)

@users_router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, user_service: UserService = Depends(lambda: UserService(get_user_repository()))):
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@users_router.get("/", response_model=List[UserRead])
async def list_users(skip: int = 0, limit: int = 10, user_service: UserService = Depends(lambda: UserService(get_user_repository()))):
    return user_service.get_users(skip, limit)

@users_router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, user: UserUpdate, user_service: UserService = Depends(lambda: UserService(get_user_repository()))):
    updated_user = user_service.update_user(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@users_router.delete("/{user_id}")
async def delete_user(user_id: int, user_service: UserService = Depends(lambda: UserService(get_user_repository()))):
    deleted = user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}