from typing import Optional
from apps.auth.models import User
from apps.auth.repository import AuthRepository
from apps.auth.schemas import UserCreate, UserUpdate, Token
from utils.security import get_password_hash, verify_password, create_access_token

class AuthService:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    def register_user(self, user_create: UserCreate) -> User:
        # 检查用户是否已存在
        existing_user = self.auth_repository.get_by_email(user_create.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # 检查用户名是否已存在
        existing_username = self.auth_repository.get_by_username(user_create.username)
        if existing_username:
            raise ValueError("User with this username already exists")
            
        # 密码哈希处理
        user_dict = user_create.dict()
        user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
        
        return self.auth_repository.create(UserCreate(**user_dict))

    def authenticate_user(self, username: str, password: str) -> Optional[Token]:
        user = self.auth_repository.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        
        # 创建访问令牌
        access_token = create_access_token(data={"sub": user.username})
        return Token(access_token=access_token, token_type="bearer")

    def get_user(self, user_id: int) -> Optional[User]:
        return self.auth_repository.get(user_id)

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        return self.auth_repository.update(user_id, user_update)

    def delete_user(self, user_id: int) -> bool:
        return self.auth_repository.delete(user_id)