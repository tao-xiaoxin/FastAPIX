from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, List, Any, Optional
from apps.auth.schemas import Token, UserCreate, UserRead, TokenPair
from apps.auth.service import AuthService
from apps.auth.dependencies import get_auth_service
from utils.response import APIResponse
from utils.token_manager import token_manager as token_mgr

async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """用户登录API"""
    token = auth_service.authenticate_user(form_data.username, form_data.password)
    if not token:
        return APIResponse.error(
            msg="用户名或密码错误", 
            code=401, 
            status_code=401, 
            headers={"WWW-Authenticate": "Bearer"}
        )
    return APIResponse.success(data=token, msg="登录成功")


async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """用户注册API"""
    try:
        user = auth_service.register_user(user_data)
        return APIResponse.success(data=user, msg="注册成功")
    except ValueError as e:
        return APIResponse.error(msg=str(e), code=400, status_code=400)


async def issue_token(
    username: str,
    password: str,
    expires_delta: Optional[int] = None,
    auth_service: AuthService = Depends(get_auth_service)
):
    """签发访问令牌API"""
    try:
        token_pair = await auth_service.issue_token(username, password, expires_delta)
        return APIResponse.success(data=token_pair, msg="令牌签发成功")
    except ValueError as e:
        return APIResponse.error(msg=str(e), code=400, status_code=400)


async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """刷新访问令牌API"""
    try:
        new_tokens = await auth_service.refresh_token(refresh_token)
        return APIResponse.success(data=new_tokens, msg="令牌刷新成功")
    except ValueError as e:
        return APIResponse.error(msg=str(e), code=400, status_code=400)


async def revoke_token(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """吊销令牌API"""
    try:
        success = await auth_service.revoke_tokens(token)
        if success:
            return APIResponse.success(data=None, msg="令牌吊销成功")
        return APIResponse.error(msg="令牌吊销失败", code=400, status_code=400)
    except ValueError as e:
        return APIResponse.error(msg=str(e), code=400, status_code=400)

# 注意：AccessKey相关的处理函数已被移除
# 令牌管理现在通过token_manager实现，并存储在Redis中
# 这种设计提供了更好的性能、安全性和水平扩展能力 