from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from apps.auth.schemas import Token, UserCreate, UserRead
from apps.auth.service import AuthService
from core.dependencies import get_auth_service
from utils.response import APIResponse

class AuthHandler:
    """认证相关的处理器，负责处理认证API请求并返回响应"""
    
    def __init__(self, auth_service: AuthService = Depends(get_auth_service)):
        self.auth_service = auth_service
    
    async def login(self, form_data: OAuth2PasswordRequestForm):
        """用户登录"""
        token = self.auth_service.authenticate_user(form_data.username, form_data.password)
        if not token:
            return APIResponse.error(
                msg="用户名或密码错误", 
                code=401, 
                status_code=401, 
                headers={"WWW-Authenticate": "Bearer"}
            )
        return APIResponse.success(data=token, msg="登录成功")
    
    async def register(self, user_data: UserCreate):
        """用户注册"""
        try:
            user = self.auth_service.register_user(user_data)
            return APIResponse.success(data=user, msg="注册成功")
        except ValueError as e:
            return APIResponse.error(msg=str(e), code=400, status_code=400) 