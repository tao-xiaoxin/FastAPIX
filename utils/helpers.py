#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用辅助工具模块
"""
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, List

logger = logging.getLogger(__name__)


def generate_uuid() -> str:
    """
    生成唯一ID
    
    Returns:
        str: 唯一ID
    """
    return str(uuid.uuid4())


def get_timestamp() -> int:
    """
    获取当前时间戳
    
    Returns:
        int: 当前时间戳(秒)
    """
    return int(datetime.now().timestamp())


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象
        format_str: 格式字符串
        
    Returns:
        str: 格式化后的日期时间字符串
    """
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    解析日期时间字符串
    
    Args:
        date_str: 日期时间字符串
        format_str: 格式字符串
        
    Returns:
        Optional[datetime]: 解析后的日期时间对象，解析失败返回None
    """
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError as e:
        logger.error(f"Date parsing error: {e}")
        return None


def filter_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    过滤字典中的None值
    
    Args:
        data: 原始字典
        
    Returns:
        Dict[str, Any]: 过滤后的字典
    """
    return {k: v for k, v in data.items() if v is not None}


def paginate(
    items: List[Any],
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    分页处理
    
    Args:
        items: 要分页的项目列表
        page: 页码(从1开始)
        page_size: 每页大小
        
    Returns:
        Dict[str, Any]: 分页结果
    """
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
        
    start = (page - 1) * page_size
    end = start + page_size
    
    total = len(items)
    data = items[start:end]
    
    return {
        "items": data,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }

def some_helper_function(param1, param2):
    # This is a placeholder for a helper function that performs a specific task.
    return param1 + param2

def another_helper_function(data):
    # This function processes the input data and returns the result.
    return { "processed_data": data }

# Additional helper functions can be added here as needed.