# FILE: /FastAPIX/FastAPIX/app/modules/auth/__init__.py
from fastapi import APIRouter

router = APIRouter()

from .router import router as auth_router

router.include_router(auth_router, prefix="/auth", tags=["auth"])