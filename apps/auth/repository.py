from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid
from apps.auth.models import User, AccessKey
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

    async def create_access_key(
        self, 
        user_id: int, 
        name: str, 
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        is_enabled: bool = True
    ) -> AccessKey:
        """
        创建访问密钥
        
        Args:
            user_id: 用户ID
            name: 密钥名称
            description: 描述
            expires_at: 过期时间
            is_enabled: 是否启用
            
        Returns:
            AccessKey: 创建的访问密钥
        """
        # 生成唯一的访问密钥
        access_key = f"ak_{uuid.uuid4().hex}"
        
        # 创建访问密钥记录
        db_key = AccessKey(
            user_id=user_id,
            name=name,
            access_key=access_key,
            description=description,
            created_at=datetime.now(),
            expires_at=expires_at,
            is_enabled=is_enabled
        )
        
        self.db.add(db_key)
        self.db.commit()
        self.db.refresh(db_key)
        
        return db_key
    
    async def get_access_keys(self, user_id: int, skip: int = 0, limit: int = 10) -> List[AccessKey]:
        """
        获取用户的访问密钥列表
        
        Args:
            user_id: 用户ID
            skip: 跳过记录数
            limit: 返回记录数
            
        Returns:
            List[AccessKey]: 访问密钥列表
        """
        return self.db.query(AccessKey).filter(
            AccessKey.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    async def get_access_key(self, key_id: int) -> Optional[AccessKey]:
        """
        通过ID获取访问密钥
        
        Args:
            key_id: 密钥ID
            
        Returns:
            Optional[AccessKey]: 访问密钥
        """
        return self.db.query(AccessKey).filter(AccessKey.id == key_id).first()
    
    async def get_access_key_by_key(self, access_key: str) -> Optional[AccessKey]:
        """
        通过密钥值获取访问密钥
        
        Args:
            access_key: 密钥值
            
        Returns:
            Optional[AccessKey]: 访问密钥
        """
        return self.db.query(AccessKey).filter(AccessKey.access_key == access_key).first()
    
    async def update_access_key(self, key_id: int, **kwargs) -> Optional[AccessKey]:
        """
        更新访问密钥
        
        Args:
            key_id: 密钥ID
            **kwargs: 更新的字段
            
        Returns:
            Optional[AccessKey]: 更新后的访问密钥
        """
        db_key = await self.get_access_key(key_id)
        if db_key:
            for key, value in kwargs.items():
                setattr(db_key, key, value)
            self.db.commit()
            self.db.refresh(db_key)
        return db_key
    
    async def update_access_key_last_used(self, key_id: int) -> Optional[AccessKey]:
        """
        更新访问密钥最后使用时间
        
        Args:
            key_id: 密钥ID
            
        Returns:
            Optional[AccessKey]: 更新后的访问密钥
        """
        return await self.update_access_key(key_id, last_used_at=datetime.now())
    
    async def delete_access_key(self, key_id: int) -> bool:
        """
        删除访问密钥
        
        Args:
            key_id: 密钥ID
            
        Returns:
            bool: 是否成功删除
        """
        db_key = await self.get_access_key(key_id)
        if db_key:
            self.db.delete(db_key)
            self.db.commit()
            return True
        return False