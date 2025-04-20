"""
数据库引擎和连接池
This file initializes the db module.
"""

from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

# 从子模块导入MySQL和Redis客户端实例
from .mysql import mysql_manager, default_db_pool, PyMySQLConnectionPool
from .redis import redis_client
from .database import Base, get_db, init_db

# 创建会话依赖
CurrentSession = Annotated[AsyncSession, Depends(mysql_manager.get_db)]

__all__ = [
    'mysql_manager',
    'default_db_pool',
    'redis_client',
    'CurrentSession',
    'PyMySQLConnectionPool',
    'Base',
    'get_db',
    'init_db'
]