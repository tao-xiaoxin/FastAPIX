from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from core.conf import settings

class UserBase(BaseModel):
    username: str
    email: EmailStr
    
class UserCreate(UserBase):
    password: str
    
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    
class UserRead(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True
        
class Token(BaseModel):
    access_token: str
    token_type: str = settings.TOKEN_TYPE
    
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = settings.TOKEN_TYPE
    