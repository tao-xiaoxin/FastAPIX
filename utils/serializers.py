#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序列化工具模块，包含自定义JSON响应
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from fastapi.responses import JSONResponse

class JsonResponse(JSONResponse):
    """
    标准JSON响应
    
    自动将响应格式化为统一的格式：
    {
        "code": 状态码,
        "message": "响应消息",
        "data": 响应数据
    }
    """
    
    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[Any] = None,
        **kwargs
    ):
        # 处理已经是标准格式的情况
        if isinstance(content, dict) and "code" in content and "message" in content:
            super().__init__(
                content=content,
                status_code=status_code,
                headers=headers,
                media_type=media_type,
                background=background
            )
            return
        
        # 处理其他情况，转换为标准格式
        formatted_content = {
            "code": status_code,
            "message": "success",
            "data": content
        }
        
        # 添加额外的字段
        if kwargs:
            for key, value in kwargs.items():
                if key not in formatted_content:
                    formatted_content[key] = value
        
        super().__init__(
            content=formatted_content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background
        )


def response_success(
    data: Any = None,
    message: str = "success",
    status_code: int = 200,
    **kwargs
) -> Dict[str, Any]:
    """
    返回成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        status_code: 状态码
        **kwargs: 其他参数
        
    Returns:
        Dict[str, Any]: 响应字典
    """
    result = {
        "code": status_code,
        "message": message,
        "data": data
    }
    
    # 添加额外的字段
    if kwargs:
        for key, value in kwargs.items():
            if key not in result:
                result[key] = value
                
    return result


def response_error(
    message: str,
    status_code: int = 400,
    detail: Optional[Any] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    返回错误响应
    
    Args:
        message: 错误消息
        status_code: 状态码
        detail: 错误详情
        **kwargs: 其他参数
        
    Returns:
        Dict[str, Any]: 响应字典
    """
    result = {
        "code": status_code,
        "message": message,
    }
    
    if detail is not None:
        result["detail"] = detail
    
    # 添加额外的字段
    if kwargs:
        for key, value in kwargs.items():
            if key not in result:
                result[key] = value
                
    return result 