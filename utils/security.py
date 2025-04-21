#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全相关工具模块，包括密码哈希和JWT令牌
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from core.conf import settings

logger = logging.getLogger(__name__)

# 密码上下文，使用bcrypt算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2认证方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    获取密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
    data: Dict[str, Any] = None
) -> str:
    """
    创建JWT访问令牌
    
    Args:
        subject: 令牌主题(通常是用户ID)
        expires_delta: 过期时间增量，默认为配置中的过期时间
        data: 额外的数据
        
    Returns:
        str: 编码后的JWT令牌
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    expire = datetime.utcnow() + expires_delta
    
    # 令牌负载
    payload = {
        "sub": str(subject),
        "exp": expire
    }
    
    # 添加额外数据
    if data:
        payload.update(data)
    
    # 使用密钥编码令牌
    encoded_jwt = jwt.encode(
        payload, 
        settings.SECRET_KEY, 
        algorithm=settings.TOKEN_ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    解码JWT访问令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        Dict[str, Any]: 解码后的令牌负载
        
    Raises:
        JWTError: 令牌无效或过期
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.TOKEN_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    获取当前用户，作为依赖注入
    
    Args:
        token: JWT令牌
        
    Returns:
        用户对象
        
    Raises:
        HTTPException: 身份验证失败
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": f"{settings.TOKEN_TYPE}"},
    )
    
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 这里应该去数据库获取用户
    # 例如: user = get_user_by_id(user_id)
    # 如果user不存在，则抛出credentials_exception
    # 由于我们还没有实现用户模型，暂时返回用户ID
    return {"id": user_id} 