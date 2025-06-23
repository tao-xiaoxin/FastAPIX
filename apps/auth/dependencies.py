#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证模块依赖注入
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from engines import AsyncDBSession
from apps.auth.repository import AuthRepository
from apps.auth.service import AuthService

def get_auth_service(db: AsyncSession = Depends(AsyncDBSession)) -> AuthService:
    """
    获取认证服务
    
    Args:
        db: 数据库会话
        
    Returns:
        AuthService: 认证服务实例
    """
    auth_repository = AuthRepository(db)
    return AuthService(auth_repository) 