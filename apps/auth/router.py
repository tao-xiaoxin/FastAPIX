from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from apps.auth.schemas import Token, UserCreate, UserRead
from apps.auth.service import AuthService
from core.dependencies import get_auth_repository
from utils.response import APIResponse

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(lambda: AuthService(get_auth_repository()))):
    token = auth_service.authenticate_user(form_data.username, form_data.password)
    if not token:
        return APIResponse.error(
            msg="用户名或密码错误", 
            code=401, 
            status_code=401, 
            headers={"WWW-Authenticate": "Bearer"}
        )
    return APIResponse.success(data=token, msg="登录成功")

@auth_router.post("/register")
async def register(user_data: UserCreate, auth_service: AuthService = Depends(lambda: AuthService(get_auth_repository()))):
    try:
        user = auth_service.register_user(user_data)
        return APIResponse.success(data=user, msg="注册成功")
    except ValueError as e:
        return APIResponse.error(msg=str(e), code=400, status_code=400)