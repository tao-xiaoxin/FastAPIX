from fastapi import APIRouter, Depends
from apps.users.schemas import UserCreate, UserUpdate
from apps.users.handlers import UserHandler
from core.dependencies import get_user_handler

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.post("/")
async def create_user(
    user: UserCreate, 
    handler: UserHandler = Depends(get_user_handler)
):
    return await handler.create_user(user)

@users_router.get("/{user_id}")
async def get_user(
    user_id: int, 
    handler: UserHandler = Depends(get_user_handler)
):
    return await handler.get_user(user_id)

@users_router.get("/")
async def list_users(
    skip: int = 0, 
    limit: int = 10, 
    handler: UserHandler = Depends(get_user_handler)
):
    return await handler.list_users(skip, limit)

@users_router.put("/{user_id}")
async def update_user(
    user_id: int, 
    user: UserUpdate, 
    handler: UserHandler = Depends(get_user_handler)
):
    return await handler.update_user(user_id, user)

@users_router.delete("/{user_id}")
async def delete_user(
    user_id: int, 
    handler: UserHandler = Depends(get_user_handler)
):
    return await handler.delete_user(user_id)