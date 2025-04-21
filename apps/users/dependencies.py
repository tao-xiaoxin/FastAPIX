#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户模块依赖注入
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from engines import AsyncDBSession
from apps.users.repository import UserRepository
from apps.users.service import UserService

def get_user_service(db: AsyncSession = Depends(AsyncDBSession)) -> UserService:
    """
    获取用户服务
    
    Args:
        db: 数据库会话
        
    Returns:
        UserService: 用户服务实例
    """
    user_repository = UserRepository(db)
    return UserService(user_repository) 