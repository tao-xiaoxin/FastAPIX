#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志模块 - 基于logru的优雅日志系统
"""
import os
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, Union, List, Callable

from logru import Logger, LogLevel, TextHandler, RotatingFileHandler
from logru.formatters import ConsoleFormatter, JsonFormatter, TextFormatter
from logru.styles import Style, Color, Decoration

from core.conf import settings

# 日志级别映射
LOG_LEVELS: Dict[str, LogLevel] = {
    "DEBUG": LogLevel.DEBUG,
    "INFO": LogLevel.INFO,
    "WARNING": LogLevel.WARN,
    "ERROR": LogLevel.ERROR,
    "CRITICAL": LogLevel.CRITICAL,
}

# 获取日志级别
LOG_LEVEL = LOG_LEVELS.get(settings.LOG_LEVEL, LogLevel.INFO)

# 创建日志目录
log_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "logs"
log_dir.mkdir(exist_ok=True)

# 定义自定义样式
STYLES = {
    "success": Style(fg=Color.GREEN, decoration=Decoration.BOLD),
    "info": Style(fg=Color.CYAN),
    "warning": Style(fg=Color.YELLOW),
    "error": Style(fg=Color.RED, decoration=Decoration.BOLD),
    "critical": Style(fg=Color.MAGENTA, decoration=Decoration.BOLD),
}

class FastAPIXLogger:
    """
    FastAPIX优雅的日志系统，基于logru实现
    
    Features:
    - 精美的终端彩色输出
    - 结构化JSON格式记录
    - 日志文件自动轮转
    - 自定义日志级别和样式
    - 上下文感知的日志记录
    - 请求跟踪与关联
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'logger'):
            # 创建logru日志器
            self.logger = Logger()
            self.configured = False
    
    def configure(self, log_file: Optional[str] = None):
        """配置日志系统"""
        if self.configured:
            return self
            
        if log_file is None:
            log_file = "fastapix.log"
        
        file_path = log_dir / log_file
        
        # 添加控制台处理器（带彩色输出）
        console_handler = TextHandler()
        
        if settings.LOG_CONSOLE_COLOR:
            console_formatter = ConsoleFormatter()
            console_formatter.level_styles = {
                LogLevel.DEBUG: STYLES["info"],
                LogLevel.INFO: STYLES["info"],
                LogLevel.WARN: STYLES["warning"],
                LogLevel.ERROR: STYLES["error"],
                LogLevel.CRITICAL: STYLES["critical"],
            }
        else:
            console_formatter = TextFormatter()
            
        console_handler.formatter = console_formatter
        
        # 添加文件处理器
        file_handler = RotatingFileHandler(
            path=str(file_path),
            max_size=settings.LOG_FILE_ROTATION,
            backup_count=settings.LOG_FILE_BACKUP_COUNT,
        )
        
        # 根据配置选择格式化器
        if settings.LOG_JSON_FORMAT:
            file_handler.formatter = JsonFormatter()
        else:
            file_handler.formatter = TextFormatter()
        
        # 设置日志级别并添加处理器
        self.logger.level = LOG_LEVEL
        self.logger.add_handler(console_handler)
        self.logger.add_handler(file_handler)
        
        self.configured = True
        self.logger.info(f"日志系统初始化完成，日志文件：{file_path}")
        return self
    
    def set_customize_logfile(self, filename: Optional[str] = None):
        """设置自定义日志文件"""
        if not filename:
            filename = "fastapix_customize.log"
        
        # 清除现有处理器
        self.logger.handlers.clear()
        self.configured = False
        
        # 使用新文件名重新配置
        return self.configure(filename)
    
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
        self.logger.warn(message, **kwargs)
        
    def error(self, message: str, **kwargs):
        self.logger.error(message, **kwargs)
        
    def critical(self, message: str, **kwargs):
        self.logger.critical(message, **kwargs)
    
    # 自定义日志方法
    def success(self, message: str, **kwargs):
        """成功日志 - 绿色标记"""
        # 使用info级别但带有success样式
        self.logger.info(message, style=STYLES["success"], **kwargs)


class ContextLogger:
    """带有上下文的日志记录器，用于在整个请求流程中跟踪特定信息"""
    
    def __init__(self, logger: Logger, context: Dict[str, Any]):
        self.logger = logger
        self.context = context
    
    def debug(self, message: str, **kwargs):
        self._log(self.logger.debug, message, **kwargs)
        
    def info(self, message: str, **kwargs):
        self._log(self.logger.info, message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        self._log(self.logger.warn, message, **kwargs)
        
    def error(self, message: str, **kwargs):
        self._log(self.logger.error, message, **kwargs)
        
    def critical(self, message: str, **kwargs):
        self._log(self.logger.critical, message, **kwargs)
        
    def success(self, message: str, **kwargs):
        self._log(self.logger.info, message, style=STYLES["success"], **kwargs)
    
    def _log(self, log_method, message: str, **kwargs):
        """合并上下文和额外参数后记录日志"""
        if not settings.LOG_INCLUDE_CONTEXT:
            # 如果配置为不包含上下文，则只记录消息
            log_method(message, **kwargs)
            return
            
        # 合并上下文，但允许kwargs覆盖相同的键
        merged_kwargs = {**self.context, **kwargs}
        log_method(message, **merged_kwargs)
    
    def with_context(self, **additional_context) -> "ContextLogger":
        """添加额外上下文"""
        merged_context = {**self.context, **additional_context}
        return ContextLogger(self.logger, merged_context)


# 创建单例实例并配置
log = FastAPIXLogger().configure() 