from sqlalchemy import Column, Integer, String, Boolean
from engines.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(Integer)  # You may want to use a DateTime type instead
    updated_at = Column(Integer)  # You may want to use a DateTime type instead