#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter
from apps.auth.router import auth_router
from apps.users.router import users_router
from core.conf import settings

routers = APIRouter(prefix=settings.API_V1_STR)
routers.include_router(auth_router)
routers.include_router(users_router)
