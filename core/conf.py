#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目配置文件
"""
import os
from pathlib import Path
from typing import List, Optional, Union, Any, Dict
from pydantic import BaseSettings, AnyHttpUrl, validator, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    # 基本配置
    PROJECT_NAME: str = "FastAPIX"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-placeholder")
    
    # 服务器设置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8099"))
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # 文档URL
    DOCS_URL: str = f"{API_V1_STR}/docs"
    REDOCS_URL: str = f"{API_V1_STR}/redoc"
    OPENAPI_URL: str = f"{API_V1_STR}/openapi.json"
    
    # CORS设置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 数据库配置
    MYSQL_SERVER: str = os.getenv("MYSQL_SERVER", "localhost")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "fastapiX")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> Any:
        if isinstance(v, str):
            return v
        user = values.get("MYSQL_USER")
        password = values.get("MYSQL_PASSWORD")
        server = values.get("MYSQL_SERVER")
        port = values.get("MYSQL_PORT")
        db = values.get("MYSQL_DB")
        
        return f"mysql+pymysql://{user}:{password}@{server}:{port}/{db}"
    
    # Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))  # 默认数据库
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    
    # Redis数据库分配
    # 每个功能使用独立的Redis数据库，提高隔离性和性能
    REDIS_DB_CACHE: int = int(os.getenv("REDIS_DB_CACHE", "1"))      # 通用缓存
    REDIS_DB_SESSION: int = int(os.getenv("REDIS_DB_SESSION", "2"))   # 会话存储
    REDIS_DB_RATE_LIMIT: int = int(os.getenv("REDIS_DB_RATE_LIMIT", "3"))  # 速率限制
    REDIS_DB_TASK_QUEUE: int = int(os.getenv("REDIS_DB_TASK_QUEUE", "4"))  # 任务队列
    
    # 中间件设置
    MIDDLEWARE_CORS: bool = os.getenv("MIDDLEWARE_CORS", "True").lower() == "true"
    MIDDLEWARE_ACCESS: bool = os.getenv("MIDDLEWARE_ACCESS", "True").lower() == "true"
    MIDDLEWARE_RATE_LIMIT: bool = os.getenv("MIDDLEWARE_RATE_LIMIT", "True").lower() == "true"
    
    # 速率限制设置
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))  # 每时间窗口最大请求数
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))      # 时间窗口大小（秒）
    RATE_LIMIT_REDIS_DB: int = REDIS_DB_RATE_LIMIT  # 使用专用的Redis数据库
    
    # 令牌设置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        

settings = Settings() 