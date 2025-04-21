from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from apps.auth.schemas import UserCreate
from apps.auth.handlers import AuthHandler
from core.dependencies import get_auth_handler

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    handler: AuthHandler = Depends(get_auth_handler)
):
    return await handler.login(form_data)

@auth_router.post("/register")
async def register(
    user_data: UserCreate,
    handler: AuthHandler = Depends(get_auth_handler)
):
    return await handler.register(user_data)