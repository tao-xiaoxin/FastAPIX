from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

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
        orm_mode = True
        
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
class AccessKeyCreate(BaseModel):
    username: str
    password: str
    name: str
    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    
class AccessKeyResponse(BaseModel):
    id: int
    user_id: int
    name: str
    access_key: str
    description: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    is_enabled: bool
    
    class Config:
        orm_mode = True