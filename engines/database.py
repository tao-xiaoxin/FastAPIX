#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接模块，负责与MySQL数据库的交互
"""
import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from config.settings import settings

logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=False,
    future=True
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# 创建Base类，所有模型都将继承此类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    提供数据库会话依赖
    使用生成器模式确保连接在使用后正确关闭
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    finally:
        db.close()
        logger.debug("Database session closed")


def init_db() -> None:
    """
    初始化数据库
    创建所有表和初始数据
    """
    try:
        # 创建所有未创建的表
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise 