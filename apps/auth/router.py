from fastapi import APIRouter
from app.modules.auth.schemas import AuthSchema
from app.modules.auth.service import AuthService

router = APIRouter()

@router.post("/login", response_model=AuthSchema)
async def login(auth_data: AuthSchema):
    return await AuthService.login(auth_data)

@router.post("/register", response_model=AuthSchema)
async def register(auth_data: AuthSchema):
    return await AuthService.register(auth_data)