#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖注入功能
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from engines.mysql import MySQLManager
from apps.auth.repository import AuthRepository
from apps.users.repository import UserRepository

def get_db():
    return MySQLManager().get_db()

def get_auth_repository(db: Session = Depends(get_db)) -> AuthRepository:
    return AuthRepository(db)

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db) 