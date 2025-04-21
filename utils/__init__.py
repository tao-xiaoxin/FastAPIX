#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具模块
"""
from utils.log import log
from utils.security import (
    verify_password, 
    get_password_hash,
    create_access_token,
    decode_access_token,
    get_current_user
)
from utils.exception import register_exception
from utils.serializers import JsonResponse, response_success, response_error

# 为了与旧版API兼容，提供别名
setup_logging = log.configure
set_customize_logfile = log.set_customize_logfile

__all__ = [
    "log",
    "setup_logging",
    "set_customize_logfile",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "register_exception",
    "JsonResponse",
    "response_success",
    "response_error"
]