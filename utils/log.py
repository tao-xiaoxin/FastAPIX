#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志模块
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from core.conf import settings

# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# 获取日志级别
LOG_LEVEL = LOG_LEVELS.get(settings.LOG_LEVEL, logging.INFO)

# 设置日志格式
log_formatter = logging.Formatter(settings.LOG_FORMAT)

# 创建日志目录
log_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "logs"
log_dir.mkdir(exist_ok=True)

# 创建日志记录器
log = logging.getLogger("fastapix")
log.setLevel(LOG_LEVEL)

# 控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
log.addHandler(console_handler)

# 保存原始日志方法
_orig_debug = log.debug
_orig_info = log.info
_orig_warning = log.warning
_orig_error = log.error
_orig_critical = log.critical

# 文件处理器
def setup_logging(log_file: Optional[str] = None):
    """
    设置日志系统
    
    Args:
        log_file: 日志文件名，如果不提供则使用默认名称
    """
    if log_file is None:
        log_file = "fastapix.log"
    
    file_path = log_dir / log_file
    
    # 创建文件处理器
    file_handler = RotatingFileHandler(
        file_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(log_formatter)
    
    # 添加处理器
    log.addHandler(file_handler)
    
    _orig_info(f"Logging to {file_path}")


def set_customize_logfile(filename: Optional[str] = None):
    """
    设置自定义日志文件
    
    Args:
        filename: 日志文件名，如果不提供则使用默认名称
    """
    if not filename:
        filename = "fastapix_customize.log"
    
    # 创建新的文件处理器
    setup_logging(filename)

# 颜色代码
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# 为log对象添加颜色方法
def _success(msg, *args, **kwargs):
    """成功日志 - 绿色"""
    if isinstance(msg, str):
        msg = f"{GREEN}{msg}{RESET}"
    return _orig_info(msg, *args, **kwargs)

def _info(msg, *args, **kwargs):
    """信息日志 - 青色"""
    if isinstance(msg, str):
        msg = f"{CYAN}{msg}{RESET}"
    return _orig_info(msg, *args, **kwargs)

def _warning(msg, *args, **kwargs):
    """警告日志 - 黄色"""
    if isinstance(msg, str):
        msg = f"{YELLOW}{msg}{RESET}"
    return _orig_warning(msg, *args, **kwargs)

def _error(msg, *args, **kwargs):
    """错误日志 - 红色"""
    if isinstance(msg, str):
        msg = f"{RED}{BOLD}{msg}{RESET}"
    return _orig_error(msg, *args, **kwargs)

def _debug(msg, *args, **kwargs):
    """调试日志 - 正常色"""
    return _orig_debug(msg, *args, **kwargs)

# 添加彩色日志方法
log.success = _success
log.info = _info
log.warning = _warning
log.error = _error
log.debug = _debug

# 默认设置
setup_logging() 