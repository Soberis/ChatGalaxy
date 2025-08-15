#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 数据库连接模块

管理Supabase数据库连接和操作:
- Supabase客户端初始化
- 数据库连接池管理
- 数据库操作封装
- 连接健康检查
"""

import asyncio
from typing import Optional, Dict, Any
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
import logging
from functools import lru_cache

from .config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    数据库管理器
    
    负责管理Supabase数据库连接和基础操作
    """
    
    def __init__(self):
        """
        初始化数据库管理器
        """
        self._client: Optional[Client] = None
        self._is_connected: bool = False
    
    async def connect(self) -> bool:
        """
        建立数据库连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
                logger.error("❌ Supabase配置不完整，无法建立连接")
                return False
            
            # 创建Supabase客户端
            options = ClientOptions(
                auto_refresh_token=True,
                persist_session=True
            )
            
            self._client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY,
                options=options
            )
            
            # 测试连接
            await self.health_check()
            
            self._is_connected = True
            logger.info("✅ Supabase数据库连接成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            self._is_connected = False
            return False
    
    async def disconnect(self):
        """
        断开数据库连接
        """
        if self._client:
            try:
                # Supabase客户端会自动处理连接清理
                self._client = None
                self._is_connected = False
                logger.info("✅ 数据库连接已断开")
            except Exception as e:
                logger.error(f"❌ 断开数据库连接时出错: {e}")
    
    async def health_check(self) -> bool:
        """
        数据库健康检查
        
        Returns:
            bool: 数据库是否健康
        """
        try:
            if not self._client:
                return False
            
            # 执行简单查询测试连接
            self._client.table('users').select('id').limit(1).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据库健康检查失败: {e}")
            return False
    
    @property
    def client(self) -> Optional[Client]:
        """
        获取Supabase客户端实例
        
        Returns:
            Optional[Client]: Supabase客户端
        """
        return self._client
    
    @property
    def is_connected(self) -> bool:
        """
        检查是否已连接
        
        Returns:
            bool: 是否已连接
        """
        return self._is_connected
    
    async def execute_query(self, table: str, operation: str, **kwargs) -> Dict[str, Any]:
        """
        执行数据库查询
        
        Args:
            table: 表名
            operation: 操作类型 (select, insert, update, delete)
            **kwargs: 查询参数
            
        Returns:
            Dict[str, Any]: 查询结果
        """
        try:
            if not self._client:
                raise Exception("数据库未连接")
            
            table_ref = self._client.table(table)
            
            if operation == "select":
                query = table_ref.select(kwargs.get('columns', '*'))
                if 'filter' in kwargs:
                    for key, value in kwargs['filter'].items():
                        query = query.eq(key, value)
                if 'limit' in kwargs:
                    query = query.limit(kwargs['limit'])
                if 'order' in kwargs:
                    query = query.order(kwargs['order'])
                
                result = query.execute()
                
            elif operation == "insert":
                result = table_ref.insert(kwargs.get('data', {})).execute()
                
            elif operation == "update":
                query = table_ref.update(kwargs.get('data', {}))
                if 'filter' in kwargs:
                    for key, value in kwargs['filter'].items():
                        query = query.eq(key, value)
                result = query.execute()
                
            elif operation == "delete":
                query = table_ref.delete()
                if 'filter' in kwargs:
                    for key, value in kwargs['filter'].items():
                        query = query.eq(key, value)
                result = query.execute()
                
            else:
                raise ValueError(f"不支持的操作类型: {operation}")
            
            return {
                "success": True,
                "data": result.data,
                "count": result.count if hasattr(result, 'count') else len(result.data or [])
            }
            
        except Exception as e:
            logger.error(f"❌ 数据库查询失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }


# 全局数据库管理器实例
db_manager = DatabaseManager()


@lru_cache()
def get_database() -> DatabaseManager:
    """
    获取数据库管理器实例
    
    Returns:
        DatabaseManager: 数据库管理器
    """
    return db_manager


async def init_database() -> bool:
    """
    初始化数据库连接
    
    Returns:
        bool: 初始化是否成功
    """
    logger.info("🔄 正在初始化数据库连接...")
    
    success = await db_manager.connect()
    
    if success:
        logger.info("✅ 数据库初始化完成")
    else:
        logger.error("❌ 数据库初始化失败")
    
    return success


async def close_database():
    """
    关闭数据库连接
    """
    logger.info("🔄 正在关闭数据库连接...")
    await db_manager.disconnect()
    logger.info("✅ 数据库连接已关闭")


# 数据库依赖注入函数
def get_db_client() -> Optional[Client]:
    """
    获取数据库客户端(用于FastAPI依赖注入)
    
    Returns:
        Optional[Client]: Supabase客户端
    """
    return db_manager.client


if __name__ == "__main__":
    """
    测试数据库连接
    """
    async def test_connection():
        """
        测试数据库连接功能
        """
        print("🧪 测试数据库连接...")
        
        # 初始化连接
        success = await init_database()
        
        if success:
            # 健康检查
            health = await db_manager.health_check()
            print(f"健康检查: {'✅ 通过' if health else '❌ 失败'}")
            
            # 关闭连接
            await close_database()
        
        print("🏁 测试完成")
    
    # 运行测试
    asyncio.run(test_connection())