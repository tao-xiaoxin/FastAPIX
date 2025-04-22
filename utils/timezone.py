#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时区和时间操作工具类
Created by: tao-xiaoxin
Created time: 2025-02-17 02:29:18
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Union
from core.conf import settings

logger = logging.getLogger(__name__)


class TimeZone:
    """时区和时间操作工具类"""

    def __init__(self, tz_offset: int = 8):
        """
        初始化时区工具类

        Args:
            tz_offset: 时区偏移小时数，默认为8（UTC+8，中国标准时间）
        """
        self.tz_offset = tz_offset
        self.tz_info = timezone(timedelta(hours=tz_offset))
    
    @property
    def now(self) -> datetime:
        """
        获取当前时区时间

        Returns:
            datetime: 当前时区的时间
        """
        return datetime.now(self.tz_info)

    def f_datetime(self, dt: datetime) -> datetime:
        """
        将datetime对象转换为指定时区的时间

        Args:
            dt: 要转换的datetime对象

        Returns:
            datetime: 转换后的时区时间

        Raises:
            ValueError: 如果输入的datetime对象没有时区信息且不是naive时间
        """
        if dt.tzinfo is None:
            # 处理naive datetime
            return dt.replace(tzinfo=self.tz_info)
        return dt.astimezone(self.tz_info)

    def f_str(
            self,
            date_str: str,
            format_str: Optional[str] = None
    ) -> datetime:
        """
        将时间字符串转换为指定时区的时间

        Args:
            date_str: 时间字符串
            format_str: 时间格式字符串，默认使用配置中的格式

        Returns:
            datetime: 转换后的时区时间

        Raises:
            ValueError: 如果时间字符串格式不正确
        """
        if format_str is None:
            format_str = settings.DATETIME_FORMAT

        try:
            dt = datetime.strptime(date_str, format_str)
            return dt.replace(tzinfo=self.tz_info)
        except ValueError as e:
            raise ValueError(f"Invalid date string format: {date_str}") from e

    def format(
            self,
            dt: Union[datetime, str],
            format_str: Optional[str] = None
    ) -> str:
        """
        将时间格式化为字符串

        Args:
            dt: datetime对象或时间字符串
            format_str: 输出格式，默认使用配置中的格式

        Returns:
            str: 格式化后的时间字符串
        """
        if format_str is None:
            format_str = settings.DATETIME_FORMAT

        if isinstance(dt, str):
            dt = self.f_str(dt)
        elif isinstance(dt, datetime):
            dt = self.f_datetime(dt)
        else:
            raise TypeError(f"Unsupported type for dt: {type(dt)}")

        return dt.strftime(format_str)

    @property
    def utc_now(self) -> datetime:
        """
        获取当前UTC时间

        Returns:
            datetime: 当前UTC时间
        """
        return datetime.now(timezone.utc)
    
    def get_timestamp(self) -> int:
        """
        获取当前时间戳
        
        Returns:
            int: 当前时间戳(秒)
        """
        return int(self.now.timestamp())
    
    def format_datetime(self, dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        格式化日期时间
        
        Args:
            dt: 日期时间对象
            format_str: 格式字符串
            
        Returns:
            str: 格式化后的日期时间字符串
        """
        return dt.strftime(format_str)
    
    def parse_datetime(self, date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
        """
        解析日期时间字符串
        
        Args:
            date_str: 日期时间字符串
            format_str: 格式字符串
            
        Returns:
            Optional[datetime]: 解析后的日期时间对象，解析失败返回None
        """
        try:
            dt = datetime.strptime(date_str, format_str)
            return self.f_datetime(dt)  # 添加时区信息
        except ValueError as e:
            logger.error(f"Date parsing error: {e}")
            return None


# 创建默认时区实例
timezone = TimeZone()

# 兼容性导出：为了不破坏现有代码，提供与helpers.py中相同的函数接口
def get_timestamp() -> int:
    """获取当前时间戳"""
    return timezone.get_timestamp()

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间"""
    return timezone.format_datetime(dt, format_str)

def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """解析日期时间字符串"""
    return timezone.parse_datetime(date_str, format_str) 