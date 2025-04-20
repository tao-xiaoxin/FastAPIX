#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目配置文件
"""
import os
from pathlib import Path
from typing import List, Optional, Union, Any, Dict
from pydantic import validator, AnyHttpUrl, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 基本配置
    PROJECT_NAME: str = "FastAPIX"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-placeholder")
    
    # 环境配置
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "dev")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # 服务器设置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8099"))
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    WORKERS: int = int(os.getenv("WORKERS", "1"))
    
    # 文档URL
    DOCS_URL: str = f"{API_V1_STR}/docs"
    REDOCS_URL: str = f"{API_V1_STR}/redoc"
    OPENAPI_URL: str = f"{API_V1_STR}/openapi.json"
    
    # CORS设置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # MySQL配置
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "fastapiX")
    MYSQL_CHARSET: str = os.getenv("MYSQL_CHARSET", "utf8mb4")
    MYSQL_ECHO: bool = os.getenv("MYSQL_ECHO", "False").lower() == "true"
    MYSQL_POOL_SIZE: int = int(os.getenv("MYSQL_POOL_SIZE", "5"))
    MYSQL_MAX_OVERFLOW: int = int(os.getenv("MYSQL_MAX_OVERFLOW", "10"))
    MYSQL_POOL_RECYCLE: int = int(os.getenv("MYSQL_POOL_RECYCLE", "3600"))
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        
        values = info.data
        user = values.get("MYSQL_USER")
        password = values.get("MYSQL_PASSWORD")
        host = values.get("MYSQL_HOST")
        port = values.get("MYSQL_PORT")
        db = values.get("MYSQL_DATABASE")
        
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    
    # Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))  # 默认数据库
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    REDIS_TIMEOUT: int = int(os.getenv("REDIS_TIMEOUT", "5"))
    REDIS_MAX_CONNECTIONS: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))
    REDIS_RETRY_ON_TIMEOUT: bool = os.getenv("REDIS_RETRY_ON_TIMEOUT", "True").lower() == "true"
    REDIS_KEY_PREFIX: str = os.getenv("REDIS_KEY_PREFIX", "fastapix:")
    REDIS_DEFAULT_EXPIRE: int = int(os.getenv("REDIS_DEFAULT_EXPIRE", "86400"))
    
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
    TOKEN_SECRET_KEY: str = os.getenv("TOKEN_SECRET_KEY", "your-token-secret-key-placeholder")
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 七牛云配置
    QINIU_ACCESS_KEY: Optional[str] = os.getenv("QINIU_ACCESS_KEY")
    QINIU_SECRET_KEY: Optional[str] = os.getenv("QINIU_SECRET_KEY")
    QINIU_BUCKET_NAME: Optional[str] = os.getenv("QINIU_BUCKET_NAME")
    QINIU_DOMAIN: Optional[str] = os.getenv("QINIU_DOMAIN")
    QINIU_BUSINESS_MEDIA_PATH: Optional[str] = os.getenv("QINIU_BUSINESS_MEDIA_PATH")
    
    # 其他配置
    OPERA_LOG_ENCRYPT_SECRET_KEY: Optional[str] = os.getenv("OPERA_LOG_ENCRYPT_SECRET_KEY")
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "ignore"  # 允许额外的字段，不会引发验证错误
    }


settings = Settings() 