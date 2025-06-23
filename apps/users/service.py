from typing import List, Optional
from apps.users.models import User
from apps.users.repository import UserRepository
from apps.users.schemas import UserCreate, UserUpdate

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user_create: UserCreate) -> User:
        return self.user_repository.create(user_create)

    def get_user(self, user_id: int) -> Optional[User]:
        return self.user_repository.get(user_id)

    def get_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        return self.user_repository.get_all(skip, limit)

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        return self.user_repository.update(user_id, user_update)

    def delete_user(self, user_id: int) -> bool:
        return self.user_repository.delete(user_id)