from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from apps.auth.schemas import Token, UserCreate, UserRead
from apps.auth.service import AuthService
from core.dependencies import get_auth_repository

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(lambda: AuthService(get_auth_repository()))):
    token = auth_service.authenticate_user(form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@auth_router.post("/register", response_model=UserRead)
async def register(user_data: UserCreate, auth_service: AuthService = Depends(lambda: AuthService(get_auth_repository()))):
    try:
        return auth_service.register_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))