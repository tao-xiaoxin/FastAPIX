"""
MySQL数据库引擎和连接池
Created by: tao-xiaoxin
"""
import sys
from typing import Any, Dict, List, Union, Tuple, AsyncGenerator, Annotated, Optional, Type
from dbutils.pooled_db import PooledDB
import pymysql
from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from fastapi import Depends
from utils.log import log
from core.conf import settings


class MySQLManager:
    """数据库管理类 - 处理SQLAlchemy异步会话"""
    
    def __init__(self):
        """初始化数据库管理器"""
        self.engine = None
        self.async_session = None
        self.initialized = False
        self.database_url = (
            f'mysql+asyncmy://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}'
            f'@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}'
            f'?charset={settings.MYSQL_CHARSET}'
        )

    async def init_database(self) -> None:
        """初始化数据库连接"""
        if self.initialized:
            return

        try:
            # 检查必要的包是否已安装
            try:
                import asyncmy
            except ImportError:
                log.error('❌ Required package "asyncmy" is not installed. Please run: pip install asyncmy')
                return

            self.engine = create_async_engine(
                self.database_url,
                echo=settings.MYSQL_ECHO,
                pool_pre_ping=True,
                pool_size=settings.MYSQL_POOL_SIZE,
                max_overflow=settings.MYSQL_MAX_OVERFLOW
            )

            self.async_session = async_sessionmaker(
                bind=self.engine,
                autoflush=False,
                expire_on_commit=False
            )

            # 测试连接
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            self.initialized = True
            log.success('✅ Database connection established successfully')

        except Exception as e:
            log.error(f'❌ Database connection failed: {str(e)}')
            if "Access denied" in str(e):
                log.error('❌ Database access denied. Please check your credentials.')
            elif "Can't connect" in str(e):
                log.error('❌ Cannot connect to database. Please check if the database server is running.')

    async def close_database(self) -> None:
        """关闭数据库连接"""
        if self.engine:
            await self.engine.dispose()
            self.initialized = False
            log.success('✅ Database connection closed successfully')

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        """
        获取数据库会话的依赖函数

        Yields:
            AsyncSession: 异步数据库会话对象
        """
        if not self.initialized:
            await self.init_database()

        session = self.async_session()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


class PyMySQLConnectionPool:
    def __init__(self, db_name: str = settings.MYSQL_DATABASE):
        """
        初始化MySQL连接池

        Args:
            db_name: 数据库名称
        """
        self.cursor = None
        self.conn = None
        try:
            self.pool = PooledDB(
                creator=pymysql,  # 使用链接数据库的模块
                maxconnections=10,  # 连接池允许的最大连接数，0和None表示不限制连接数
                mincached=5,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
                maxcached=20,  # 链接池中最多闲置的链接，0和None不限制
                maxshared=3,  # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql的threadsafety为1，所有链接都是独享的。
                blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
                maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
                setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
                ping=1,  # ping MySQL服务端，检查是否服务可用。
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=db_name,
                charset=settings.MYSQL_CHARSET
            )
            self.db_name = db_name
            log.success(f"✅ Successfully initialized MySQL connection pool for database: {db_name}")
        except Exception as e:
            log.error(f"❌ Failed to initialize MySQL connection pool: {str(e)}")
            raise

    def open(self) -> Tuple[Any, Any]:
        """
        获取数据库连接和游标

        Returns:
            Tuple[Connection, Cursor]: 数据库连接和游标对象
        """
        try:
            self.conn = self.pool.connection()
            self.cursor = self.conn.cursor()
            return self.conn, self.cursor
        except Exception as e:
            log.error(f"❌ Failed to open database connection: {str(e)}")
            raise

    def get_connection(self) -> Any:
        """
        获取数据库连接

        Returns:
            Connection: 数据库连接对象
        """
        try:
            return self.pool.connection()
        except Exception as e:
            log.error(f"❌ Failed to get database connection: {str(e)}")
            raise

    @staticmethod
    def close(cursor: Any, conn: Any) -> None:
        """
        关闭数据库连接和游标

        Args:
            cursor: 游标对象
            conn: 数据库连接对象
        """
        try:
            cursor.close()
            conn.close()
        except Exception as e:
            log.error(f"❌ Failed to close database connection: {str(e)}")
            raise

    def select_one(self, sql: str) -> Optional[tuple]:
        """
        查询单条数据

        Args:
            sql: SQL查询语句

        Returns:
            Optional[tuple]: 查询结果
        """
        try:
            conn, cursor = self.open()
            log.debug(f"Executing SQL: {sql}")
            cursor.execute(sql)
            result = cursor.fetchone()
            self.close(cursor, conn)
            log.success(f"✅ Successfully executed select_one query")
            return result
        except Exception as e:
            log.error(f"❌ Failed to execute select_one query: {str(e)}\nSQL: {sql}")
            raise

    def select_all(self, sql: str) -> List[tuple]:
        """
        查询多条数据

        Args:
            sql: SQL查询语句

        Returns:
            List[tuple]: 查询结果列表
        """
        try:
            conn, cursor = self.open()
            log.debug(f"Executing SQL: {sql}")
            cursor.execute(sql)
            result = cursor.fetchall()
            self.close(cursor, conn)
            log.success(f"✅ Successfully executed select_all query")
            return result
        except Exception as e:
            log.error(f"❌ Failed to execute select_all query: {str(e)}\nSQL: {sql}")
            raise

    def insert_one(self, sql: str) -> None:
        """
        插入单条数据

        Args:
            sql: SQL插入语句
        """
        try:
            self.execute(sql, is_need_rollback=False)
            log.success(f"✅ Successfully inserted one record")
        except Exception as e:
            log.error(f"❌ Failed to insert one record: {str(e)}\nSQL: {sql}")
            raise

    def insert_all(self, sql: str, datas: List[tuple]) -> Dict[str, Any]:
        """
        批量插入数据

        Args:
            sql: SQL插入语句
            datas: 要插入的数据列表

        Returns:
            Dict[str, Any]: 插入结果
        """
        conn, cursor = self.open()
        try:
            log.debug(f"Executing batch insert SQL: {sql}")
            cursor.executemany(sql, datas)
            conn.commit()
            result = {'result': True, 'id': int(cursor.lastrowid)}
            log.success(f"✅ Successfully inserted {len(datas)} records")
            return result
        except Exception as e:
            conn.rollback()
            log.error(f"❌ Failed to execute batch insert: {str(e)}\nSQL: {sql}")
            return {'result': False, 'err': str(e)}
        finally:
            self.close(cursor, conn)

    def update_one(self, sql: str) -> None:
        """
        更新数据

        Args:
            sql: SQL更新语句
        """
        try:
            self.execute(sql, is_need_rollback=True)
            log.success(f"✅ Successfully updated record")
        except Exception as e:
            log.error(f"❌ Failed to update record: {str(e)}\nSQL: {sql}")
            raise

    def delete_one(self, sql: str) -> None:
        """
        删除数据

        Args:
            sql: SQL删除语句
        """
        try:
            self.execute(sql, is_need_rollback=True)
            log.success(f"✅ Successfully deleted record")
        except Exception as e:
            log.error(f"❌ Failed to delete record: {str(e)}\nSQL: {sql}")
            raise

    def execute(self, sql: str, is_need_rollback: bool = False) -> None:
        """
        执行SQL语句

        Args:
            sql: SQL语句
            is_need_rollback: 是否需要回滚
        """
        conn, cursor = self.open()
        try:
            log.debug(f"Executing SQL: {sql}")
            cursor.execute(sql)
            conn.commit()
            log.success(f"✅ Successfully executed SQL statement")
        except Exception as e:
            if is_need_rollback:
                conn.rollback()
                log.warning(f"⚠️ Transaction rolled back")
            log.error(f"❌ Failed to execute SQL: {str(e)}\nSQL: {sql}")
            raise
        finally:
            self.close(cursor, conn)


# 创建全局 MySQL 管理器实例
mysql_manager = MySQLManager()
# 创建会话依赖
CurrentSession = Annotated[AsyncSession, Depends(mysql_manager.get_db)]
# 创建默认数据库连接池实例
default_db_pool = PyMySQLConnectionPool()