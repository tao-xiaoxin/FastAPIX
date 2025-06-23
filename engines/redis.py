#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis数据库引擎和连接模块
Created by: tao-xiaoxin
"""
import sys
from typing import Any, Dict, List, Union, Optional
from redis.asyncio.client import Redis
from redis.exceptions import AuthenticationError, TimeoutError
from utils.log import log
from core.conf import settings


class RedisClient:
    """Redis 客户端，支持多数据库操作"""

    def __init__(self):
        """初始化 Redis 客户端"""
        self._clients = {}
        self._default_db = settings.REDIS_DB
        self._default_client = self._create_client(self._default_db)

    def _create_client(self, db: int) -> Redis:
        """
        创建Redis客户端

        Args:
            db: Redis数据库索引

        Returns:
            Redis: Redis客户端实例
        """
        return Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=db,
            socket_timeout=settings.REDIS_TIMEOUT,
            decode_responses=True,  # 转码 utf-8
        )

    def _get_client(self, db: Optional[int] = None) -> Redis:
        """
        获取指定数据库的Redis客户端

        Args:
            db: Redis数据库索引，如果为None则使用默认数据库

        Returns:
            Redis: Redis客户端实例
        """
        db = self._default_db if db is None else db
        
        if db not in self._clients:
            self._clients[db] = self._create_client(db)
        
        return self._clients[db]

    async def open(self) -> None:
        """
        触发初始化连接
        """
        try:
            await self._default_client.ping()
            log.success('✅ Redis connection established successfully')
        except TimeoutError:
            log.error('❌ Redis connection timeout')
            sys.exit(1)
        except AuthenticationError:
            log.error('❌ Redis authentication failed')
            sys.exit(1)
        except Exception as e:
            log.error('❌ Redis connection error: {}', str(e))
            sys.exit(1)

    async def close(self) -> None:
        """
        关闭所有Redis连接
        """
        for db, client in self._clients.items():
            try:
                await client.close()
                log.info(f'Redis connection closed for DB {db}')
            except Exception as e:
                log.error(f'Failed to close Redis connection for DB {db}: {str(e)}')
        
        self._clients.clear()

    async def delete_prefix(self, prefix: str, exclude: Optional[Union[str, List[str]]] = None, db: Optional[int] = None) -> None:
        """
        删除指定前缀的所有key

        Args:
            prefix: key前缀
            exclude: 排除的key或key列表
            db: Redis数据库索引，如果为None则使用默认数据库
        """
        client = self._get_client(db)
        try:
            keys = []
            async for key in client.scan_iter(match=f'{prefix}*'):
                if isinstance(exclude, str):
                    if key != exclude:
                        keys.append(key)
                elif isinstance(exclude, list):
                    if key not in exclude:
                        keys.append(key)
                else:
                    keys.append(key)

            if keys:
                await client.delete(*keys)
                log.success(f'✅ Successfully deleted {len(keys)} keys with prefix: {prefix} in DB {db or self._default_db}')
            else:
                log.info(f'No keys found with prefix: {prefix} in DB {db or self._default_db}')
        except Exception as e:
            log.error(f'❌ Failed to delete keys with prefix {prefix} in DB {db or self._default_db}: {str(e)}')

    async def delete_key(self, key: str, db: Optional[int] = None) -> bool:
        """
        删除单个key

        Args:
            key: 要删除的key
            db: Redis数据库索引，如果为None则使用默认数据库

        Returns:
            bool: 删除是否成功
        """
        client = self._get_client(db)
        try:
            result = await client.delete(key)
            if result:
                log.success(f'✅ Successfully deleted key: {key} in DB {db or self._default_db}')
            else:
                log.info(f'Key not found: {key} in DB {db or self._default_db}')
            return bool(result)
        except Exception as e:
            log.error(f'❌ Failed to delete key {key} in DB {db or self._default_db}: {str(e)}')
            return False

    async def set_key(
            self,
            key: str,
            value: Any,
            expire: Optional[int] = settings.REDIS_DEFAULT_EXPIRE,
            nx: bool = False,
            xx: bool = False,
            db: Optional[int] = None
    ) -> bool:
        """
        设置key的值

        Args:
            key: 键名
            value: 值
            expire: 过期时间(秒)
            nx: 如果设置为True，只有key不存在时才会设置key的值
            xx: 如果设置为True，只有key存在时才会设置key的值
            db: Redis数据库索引，如果为None则使用默认数据库

        Returns:
            bool: 设置是否成功
        """
        client = self._get_client(db)
        try:
            result = await client.set(
                key,
                value,
                ex=expire,
                nx=nx,
                xx=xx
            )
            if result:
                log.success(f'✅ Successfully set key: {key} in DB {db or self._default_db}')
                if expire:
                    log.info(f'Key {key} will expire in {expire} seconds')
            else:
                log.warning(f'⚠️ Failed to set key: {key} in DB {db or self._default_db}')
            return bool(result)
        except Exception as e:
            log.error(f'❌ Failed to set key {key} in DB {db or self._default_db}: {str(e)}')
            return False

    async def get_key(self, key: str, db: Optional[int] = None) -> Optional[Any]:
        """
        获取key的值

        Args:
            key: 键名
            db: Redis数据库索引，如果为None则使用默认数据库

        Returns:
            Any: key的值，如果key不存在则返回None
        """
        client = self._get_client(db)
        try:
            value = await client.get(key)
            if value is not None:
                log.success(f'✅ Successfully got value for key: {key} from DB {db or self._default_db}')
            else:
                log.info(f'Key not found: {key} in DB {db or self._default_db}')
            return value
        except Exception as e:
            log.error(f'❌ Failed to get key {key} from DB {db or self._default_db}: {str(e)}')
            return None

    async def set_key_with_ttl(
            self,
            key: str,
            value: Any,
            ttl: int,
            nx: bool = False,
            xx: bool = False,
            db: Optional[int] = None
    ) -> bool:
        """
        设置key的值和过期时间

        Args:
            key: 键名
            value: 值
            ttl: 过期时间(秒)
            nx: 如果设置为True，只有key不存在时才会设置key的值
            xx: 如果设置为True，只有key存在时才会设置key的值
            db: Redis数据库索引，如果为None则使用默认数据库

        Returns:
            bool: 设置是否成功
        """
        return await self.set_key(key, value, expire=ttl, nx=nx, xx=xx, db=db)


# 创建 redis 客户端实例
redis_client = RedisClient()

def get_redis_client() -> RedisClient:
    """获取Redis客户端实例"""
    return redis_client