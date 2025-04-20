# FILE: /FastAPIX/FastAPIX/app/modules/users/__init__.py
from fastapi import APIRouter

router = APIRouter()

from .router import router as user_router

router.include_router(user_router, prefix="/users", tags=["users"])