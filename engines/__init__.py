#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
引擎包初始化文件
提供数据库和Redis连接功能
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .mysql import (
    mysql_manager, 
    default_db_pool, 
    AsyncDBSession, 
    SyncDBSession, 
    Base, 
    PyMySQLConnectionPool
)
from .redis import redis_client

__all__ = [
    "mysql_manager",
    "default_db_pool",
    "AsyncDBSession",
    "SyncDBSession",
    "Base",
    "PyMySQLConnectionPool",
    "redis_client"
]