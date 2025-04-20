from fastapi import APIRouter
from app.modules.users.schemas import UserCreate, UserRead
from app.modules.users.service import UserService

router = APIRouter()
user_service = UserService()

@router.post("/users/", response_model=UserRead)
async def create_user(user: UserCreate):
    return await user_service.create_user(user)

@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(user_id: int):
    return await user_service.get_user(user_id)

@router.get("/users/", response_model=list[UserRead])
async def list_users():
    return await user_service.list_users()