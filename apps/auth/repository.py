from sqlalchemy.orm import Session
from typing import Optional
from apps.auth.models import User
from apps.auth.schemas import UserCreate, UserUpdate

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: UserCreate) -> User:
        db_user = User(**user.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def update(self, user_id: int, user: UserUpdate) -> Optional[User]:
        db_user = self.get(user_id)
        if db_user:
            for key, value in user.dict(exclude_unset=True).items():
                setattr(db_user, key, value)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    def delete(self, user_id: int) -> bool:
        db_user = self.get(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False