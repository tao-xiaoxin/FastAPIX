from typing import Optional, List
from datetime import timedelta
from apps.auth.models import User
from apps.auth.repository import AuthRepository
from apps.auth.schemas import UserCreate, UserUpdate, Token, AccessKeyCreate, AccessKeyResponse, TokenPair
from utils.security import get_password_hash, verify_password, create_access_token
from utils.token_manager import token_manager as token_mgr
from utils.log import log

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
        
    async def create_access_key(self, key_data: AccessKeyCreate) -> AccessKeyResponse:
        """
        创建访问密钥
        
        Args:
            key_data: 访问密钥创建数据
            
        Returns:
            AccessKeyResponse: 创建的访问密钥
        """
        try:
            # 检查用户
            user = self.auth_repository.get_by_username(key_data.username)
            if not user:
                raise ValueError("用户不存在")
                
            # 验证密码
            if not verify_password(key_data.password, user.hashed_password):
                raise ValueError("密码错误")
                
            # 创建访问密钥
            access_key = await self.auth_repository.create_access_key(
                user_id=user.id,
                name=key_data.name,
                description=key_data.description,
                expires_at=key_data.expires_at,
                is_enabled=True
            )
            
            return AccessKeyResponse(
                id=access_key.id,
                user_id=access_key.user_id,
                name=access_key.name,
                access_key=access_key.access_key,
                description=access_key.description,
                created_at=access_key.created_at,
                expires_at=access_key.expires_at,
                last_used_at=access_key.last_used_at,
                is_enabled=access_key.is_enabled
            )
            
        except Exception as e:
            log.error(f"Failed to create access key: {str(e)}")
            raise ValueError(f"创建访问密钥失败: {str(e)}")
            
    async def get_access_keys(self, user_id: int, skip: int = 0, limit: int = 10) -> List[AccessKeyResponse]:
        """
        获取用户的访问密钥列表
        
        Args:
            user_id: 用户ID
            skip: 跳过记录数
            limit: 返回记录数
            
        Returns:
            List[AccessKeyResponse]: 访问密钥列表
        """
        try:
            # 检查用户
            user = self.auth_repository.get(user_id)
            if not user:
                raise ValueError("用户不存在")
                
            # 获取访问密钥
            keys = await self.auth_repository.get_access_keys(user_id, skip, limit)
            
            return [
                AccessKeyResponse(
                    id=key.id,
                    user_id=key.user_id,
                    name=key.name,
                    access_key=key.access_key,
                    description=key.description,
                    created_at=key.created_at,
                    expires_at=key.expires_at,
                    last_used_at=key.last_used_at,
                    is_enabled=key.is_enabled
                ) for key in keys
            ]
            
        except Exception as e:
            log.error(f"Failed to get access keys: {str(e)}")
            raise ValueError(f"获取访问密钥失败: {str(e)}")
            
    async def issue_token(self, access_key: str, expires_delta: Optional[int] = None) -> TokenPair:
        """
        签发访问令牌
        
        Args:
            access_key: 访问密钥
            expires_delta: 令牌有效期(秒)
            
        Returns:
            TokenPair: 访问令牌和刷新令牌对
        """
        try:
            # 验证访问密钥
            key_info = await self.auth_repository.get_access_key_by_key(access_key)
            if not key_info:
                raise ValueError("访问密钥不存在")
                
            if not key_info.is_enabled:
                raise ValueError("访问密钥已禁用")
                
            # 检查过期时间
            if key_info.expires_at and key_info.expires_at < key_info.created_at:
                raise ValueError("访问密钥已过期")
                
            # 更新最后使用时间
            await self.auth_repository.update_access_key_last_used(key_info.id)
            
            # 计算过期时间
            if expires_delta:
                expiry = timedelta(seconds=expires_delta)
            else:
                expiry = None
                
            # 生成令牌对
            access_token, refresh_token = await token_mgr.generate_token_pair(
                subject=access_key,
                data={"key": access_key, "id": key_info.id, "user_id": key_info.user_id, "name": key_info.name},
                expire_time=key_info.expires_at
            )
            
            return TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )
            
        except Exception as e:
            log.error(f"Failed to issue token: {str(e)}")
            raise ValueError(f"签发令牌失败: {str(e)}")
            
    async def refresh_token(self, refresh_token: str) -> TokenPair:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            TokenPair: 新的访问令牌和刷新令牌对
        """
        try:
            # 验证刷新令牌
            token_data = await token_mgr.verify_token(refresh_token, "refresh")
            if not token_data:
                raise ValueError("无效的刷新令牌")
                
            # 获取访问密钥
            access_key = token_data.get("key")
            if not access_key:
                raise ValueError("刷新令牌不包含访问密钥信息")
                
            # 验证访问密钥
            key_info = await self.auth_repository.get_access_key_by_key(access_key)
            if not key_info:
                raise ValueError("访问密钥不存在")
                
            if not key_info.is_enabled:
                raise ValueError("访问密钥已禁用")
                
            # 撤销旧的刷新令牌
            await token_mgr.revoke_token(refresh_token, "refresh")
            
            # 生成新的令牌对
            access_token, new_refresh_token = await token_mgr.generate_token_pair(
                subject=access_key,
                data={"key": access_key, "id": key_info.id, "user_id": key_info.user_id, "name": key_info.name},
                expire_time=key_info.expires_at
            )
            
            return TokenPair(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer"
            )
            
        except Exception as e:
            log.error(f"Failed to refresh token: {str(e)}")
            raise ValueError(f"刷新令牌失败: {str(e)}")
            
    async def revoke_tokens(self, access_key: str) -> bool:
        """
        撤销访问密钥的所有令牌
        
        Args:
            access_key: 访问密钥
            
        Returns:
            bool: 是否成功撤销
        """
        try:
            # 验证访问密钥
            key_info = await self.auth_repository.get_access_key_by_key(access_key)
            if not key_info:
                raise ValueError("访问密钥不存在")
            
            # 撤销所有令牌
            return await token_mgr.revoke_tokens(access_key)
            
        except Exception as e:
            log.error(f"Failed to revoke tokens: {str(e)}")
            raise ValueError(f"撤销令牌失败: {str(e)}")