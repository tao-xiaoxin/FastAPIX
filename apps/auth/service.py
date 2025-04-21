from typing import Optional, List
from datetime import timedelta
from apps.users.models import User
from apps.auth.repository import AuthRepository
from apps.auth.schemas import UserCreate, UserUpdate, Token, TokenPair
from utils.security import get_password_hash, verify_password, create_access_token
from utils.token_manager import token_manager as token_mgr
from utils.log import log
from core.conf import settings

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
        return Token(access_token=access_token, token_type=settings.TOKEN_TYPE)

    def get_user(self, user_id: int) -> Optional[User]:
        return self.auth_repository.get(user_id)

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        return self.auth_repository.update(user_id, user_update)

    def delete_user(self, user_id: int) -> bool:
        return self.auth_repository.delete(user_id)
    
    async def issue_token(self, username: str, password: str, expires_delta: Optional[int] = None) -> TokenPair:
        """
        签发访问令牌
        
        Args:
            username: 用户名
            password: 密码
            expires_delta: 令牌有效期(秒)
            
        Returns:
            TokenPair: 访问令牌和刷新令牌对
        """
        try:
            # 验证用户凭据
            user = self.auth_repository.get_by_username(username)
            if not user:
                raise ValueError("用户不存在")
                
            if not verify_password(password, user.hashed_password):
                raise ValueError("密码错误")
                
            # 计算过期时间
            if expires_delta:
                expiry = timedelta(seconds=expires_delta)
            else:
                expiry = None
                
            # 生成令牌对
            access_token, refresh_token = await token_mgr.generate_token_pair(
                subject=str(user.id),
                data={"user_id": user.id, "username": user.username, "email": user.email},
                expire_time=None
            )
            
            return TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=settings.TOKEN_TYPE
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
                
            # 提取用户ID
            user_id = token_data.get("sub")
            if not user_id:
                raise ValueError("令牌中缺少用户ID")
                
            # 检查用户是否存在
            user = self.auth_repository.get(int(user_id))
            if not user:
                raise ValueError("用户不存在")
                
            # 刷新令牌
            access_token, refresh_token = await token_mgr.refresh_tokens(
                subject=user_id,
                token=token_data.get("token", ""),
                refresh_token=refresh_token
            )
            
            return TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=settings.TOKEN_TYPE
            )
            
        except Exception as e:
            log.error(f"Failed to refresh token: {str(e)}")
            raise ValueError(f"刷新令牌失败: {str(e)}")
            
    async def revoke_tokens(self, token: str) -> bool:
        """
        吊销令牌
        
        Args:
            token: 要吊销的令牌
            
        Returns:
            bool: 是否成功吊销
        """
        try:
            # 从令牌中解析用户ID
            token_data = await token_mgr.decode_token(token)
            user_id = token_data.get("sub")
            if not user_id:
                raise ValueError("令牌中缺少用户ID")
                
            # 使用用户ID吊销所有令牌
            return await token_mgr.revoke_tokens(user_id)
        except Exception as e:
            log.error(f"Failed to revoke tokens: {str(e)}")
            raise ValueError(f"吊销令牌失败: {str(e)}")
    
    # 注意：令牌管理现在通过token_manager实现
    # 可以根据配置选择使用Redis或内存存储
    # 这种设计提供了更好的性能、安全性和灵活性