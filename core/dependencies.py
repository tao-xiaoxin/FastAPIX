#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖注入功能
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from engines.mysql import MySQLManager
from engines import AsyncDBSession, SyncDBSession
from apps.auth.repository import AuthRepository
from apps.users.repository import UserRepository
from apps.auth.service import AuthService
from apps.users.service import UserService

# 仓库层依赖
def get_auth_repository(db: AsyncSession = Depends(AsyncDBSession)) -> AuthRepository:
    return AuthRepository(db)

def get_user_repository(db: AsyncSession = Depends(AsyncDBSession)) -> UserRepository:
    return UserRepository(db)

# 服务层依赖
def get_auth_service(auth_repository: AuthRepository = Depends(get_auth_repository)) -> AuthService:
    return AuthService(auth_repository)

def get_user_service(user_repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repository) 