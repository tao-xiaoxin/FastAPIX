from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.mysql import get_db
from app.auth.repository import AuthRepository
from app.users.repository import UserRepository

def get_auth_repository(db: Session = Depends(get_db)) -> AuthRepository:
    return AuthRepository(db)

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)