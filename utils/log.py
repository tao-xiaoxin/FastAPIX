#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志模块 - 基于loguru的优雅日志系统
"""
import os
import sys
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, Union, List, Callable

from loguru import logger
from core.conf import settings

# 创建日志目录
log_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / settings.LOG_DIR
log_dir.mkdir(exist_ok=True)

# 日志级别映射
LOG_LEVELS = {
    "DEBUG": "DEBUG",
    "INFO": "INFO",
    "WARNING": "WARNING",
    "ERROR": "ERROR",
    "CRITICAL": "CRITICAL",
}

# 获取日志级别
LOG_LEVEL = LOG_LEVELS.get(settings.LOG_LEVEL, "INFO")

# 自定义格式化器函数
def formatter(record):
    # 使用配置文件中定义的格式
    format_string = settings.LOG_FORMAT
    
    # 如果有额外字段（context），添加到格式中
    if record["extra"]:
        extras = " | " + " | ".join(f"<blue>{k}</blue>: {v}" for k, v in record["extra"].items())
        format_string += extras
    
    return format_string + "\n"

class FastAPIXLogger:
    """
    FastAPIX优雅的日志系统，基于loguru实现
    
    Features:
    - 精美的终端彩色输出
    - 结构化JSON格式记录
    - 日志文件自动轮转
    - 自定义日志级别和样式
    - 上下文感知的日志记录
    - 请求跟踪与关联
    - 错误日志与一般日志分离存储
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = logger
        self.configured = False
    
    def configure(self):
        """配置日志系统"""
        if self.configured:
            return self
        
        # 移除默认处理器
        self.logger.remove()
        
        # 添加控制台处理器（带彩色输出）
        if settings.LOG_CONSOLE_COLOR:
            self.logger.add(
                sys.stderr,
                format=formatter,
                level=LOG_LEVEL,
                colorize=True,
            )
        else:
            # 无颜色版本的格式
            plain_format = settings.LOG_FORMAT.replace("<green>", "").replace("</green>", "") \
                                          .replace("<level>", "").replace("</level>", "") \
                                          .replace("<cyan>", "").replace("</cyan>", "") \
                                          .replace("<blue>", "").replace("</blue>", "")
            self.logger.add(
                sys.stderr,
                format=plain_format,
                level=LOG_LEVEL,
                colorize=False,
            )
        
        # 定义基本格式
        if settings.LOG_JSON_FORMAT:
            # JSON格式
            log_format = "{time} | {level} | {message} | {extra}"
            serialize = True
        else:
            # 文本格式 - 无颜色标签版本
            log_format = settings.LOG_FORMAT.replace("<green>", "").replace("</green>", "") \
                                      .replace("<level>", "").replace("</level>", "") \
                                      .replace("<cyan>", "").replace("</cyan>", "") \
                                      .replace("<blue>", "").replace("</blue>", "")
            serialize = False
        
        # 添加普通日志文件处理器 (DEBUG, INFO, WARNING)
        info_log_path = str(log_dir / settings.LOG_INFO_FILENAME)
        self.logger.add(
            sink=info_log_path,
            format=log_format,
            level="DEBUG",  # 从DEBUG级别开始记录
            filter=lambda record: record["level"].no < logger.level("ERROR").no,  # 只记录ERROR级别以下的日志
            rotation=settings.LOG_FILE_ROTATION,
            retention=settings.LOG_FILE_BACKUP_COUNT,
            serialize=serialize,
        )
        
        # 添加错误日志文件处理器 (ERROR, CRITICAL)
        error_log_path = str(log_dir / settings.LOG_ERROR_FILENAME)
        self.logger.add(
            sink=error_log_path,
            format=log_format,
            level="ERROR",  # 只记录ERROR及以上级别
            rotation=settings.LOG_FILE_ROTATION,
            retention=settings.LOG_FILE_BACKUP_COUNT,
            serialize=serialize,
        )
        
        self.configured = True
        return self
    
    def set_customize_logfile(self):
        """设置自定义日志文件"""
        # 从配置文件中获取自定义日志文件名
        info_filename = settings.LOG_CUSTOMIZE_INFO_FILENAME
        error_filename = settings.LOG_CUSTOMIZE_ERROR_FILENAME
        
        # 移除现有处理器
        self.logger.remove()
        self.configured = False
        
        # 添加控制台处理器（带彩色输出）
        if settings.LOG_CONSOLE_COLOR:
            self.logger.add(
                sys.stderr,
                format=formatter,
                level=LOG_LEVEL,
                colorize=True,
            )
        else:
            # 无颜色版本的格式
            plain_format = settings.LOG_FORMAT.replace("<green>", "").replace("</green>", "") \
                                          .replace("<level>", "").replace("</level>", "") \
                                          .replace("<cyan>", "").replace("</cyan>", "") \
                                          .replace("<blue>", "").replace("</blue>", "")
            self.logger.add(
                sys.stderr,
                format=plain_format,
                level=LOG_LEVEL,
                colorize=False,
            )
        
        # 定义基本格式
        if settings.LOG_JSON_FORMAT:
            # JSON格式
            log_format = "{time} | {level} | {message} | {extra}"
            serialize = True
        else:
            # 文本格式 - 无颜色标签版本
            log_format = settings.LOG_FORMAT.replace("<green>", "").replace("</green>", "") \
                                      .replace("<level>", "").replace("</level>", "") \
                                      .replace("<cyan>", "").replace("</cyan>", "") \
                                      .replace("<blue>", "").replace("</blue>", "")
            serialize = False
        
        # 添加普通日志文件处理器 (DEBUG, INFO, WARNING)
        info_log_path = str(log_dir / info_filename)
        self.logger.add(
            sink=info_log_path,
            format=log_format,
            level="DEBUG",  # 从DEBUG级别开始记录
            filter=lambda record: record["level"].no < logger.level("ERROR").no,  # 只记录ERROR级别以下的日志
            rotation=settings.LOG_FILE_ROTATION,
            retention=settings.LOG_FILE_BACKUP_COUNT,
            serialize=serialize,
        )
        
        # 添加错误日志文件处理器 (ERROR, CRITICAL)
        error_log_path = str(log_dir / error_filename)
        self.logger.add(
            sink=error_log_path,
            format=log_format,
            level="ERROR",  # 只记录ERROR及以上级别
            rotation=settings.LOG_FILE_ROTATION,
            retention=settings.LOG_FILE_BACKUP_COUNT,
            serialize=serialize,
        )
        
        self.configured = True
        self.logger.info(f"自定义日志系统初始化完成，普通日志文件：{info_log_path}，错误日志文件：{error_log_path}")
        return self
    
    def with_context(self, **context) -> "ContextLogger":
        """创建带有上下文的日志记录器"""
        return ContextLogger(self.logger, context)
    
    def with_request_id(self, request_id: Optional[str] = None) -> "ContextLogger":
        """创建带有请求ID的日志记录器，用于跟踪整个请求流程"""
        if request_id is None:
            request_id = str(uuid.uuid4())
        return self.with_context(**{settings.LOG_CONTEXT_REQUEST_ID: request_id})
    
    def with_request(self, request) -> "ContextLogger":
        """从FastAPI请求对象创建上下文日志记录器"""
        # 提取所需字段作为上下文
        context = {}
        if hasattr(request, "client") and request.client:
            context["client"] = f"{request.client.host}:{request.client.port}"
        context["method"] = request.method
        context["url"] = str(request.url)
        
        # 添加请求ID，如果请求头中没有，则生成一个
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        context[settings.LOG_CONTEXT_REQUEST_ID] = request_id
        
        return self.with_context(**context)
    
    # 标准日志方法
    def debug(self, message: str, **kwargs):
        self.logger.debug(message, **kwargs)
        
    def info(self, message: str, **kwargs):
        self.logger.info(message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, **kwargs)
        
    def error(self, message: str, **kwargs):
        self.logger.error(message, **kwargs)
        
    def critical(self, message: str, **kwargs):
        self.logger.critical(message, **kwargs)
    
    # 自定义日志方法
    def success(self, message: str, **kwargs):
        """成功日志 - 绿色标记"""
        # 使用成功级别记录日志
        self.logger.success(message, **kwargs)


class ContextLogger:
    """带有上下文的日志记录器，用于在整个请求流程中跟踪特定信息"""
    
    def __init__(self, logger, context: Dict[str, Any]):
        self.logger = logger.bind(**context)
        self.context = context
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(message, **kwargs)
        
    def info(self, message: str, **kwargs):
        self.logger.info(message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, **kwargs)
        
    def error(self, message: str, **kwargs):
        self.logger.error(message, **kwargs)
        
    def critical(self, message: str, **kwargs):
        self.logger.critical(message, **kwargs)
        
    def success(self, message: str, **kwargs):
        self.logger.success(message, **kwargs)
    
    def with_context(self, **additional_context) -> "ContextLogger":
        """添加额外上下文"""
        merged_context = {**self.context, **additional_context}
        return ContextLogger(self.logger.parent, merged_context)


# 创建单例实例并配置
log = FastAPIXLogger().configure() 