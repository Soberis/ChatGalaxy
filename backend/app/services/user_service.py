#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 用户服务模块

提供用户管理相关的业务逻辑:
- 用户注册和登录
- 用户信息管理
- 用户状态管理
- 用户数据验证
"""

from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import logging

from ..core.database import DatabaseManager
from ..core.security import SecurityManager
from ..models.user import (
    User, UserCreate, UserUpdate, UserResponse
)
from ..models.auth import (
    RegisterRequest, LoginRequest, TokenResponse
)


class UserService:
    """
    用户服务类
    
    提供用户管理的核心业务逻辑
    """
    
    def __init__(self, db: DatabaseManager, security: SecurityManager):
        """
        初始化用户服务
        
        Args:
            db: 数据库管理器
            security: 安全管理器
        """
        self.db = db
        self.security = security
        self.logger = logging.getLogger(__name__)
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        创建新用户
        
        Args:
            user_data: 用户创建数据
            
        Returns:
            UserResponse: 创建的用户信息
            
        Raises:
            ValueError: 用户数据验证失败
            Exception: 数据库操作失败
        """
        try:
            # 验证密码一致性
            if user_data.password != user_data.confirm_password:
                raise ValueError("密码和确认密码不一致")
            
            # 检查邮箱是否已存在
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                raise ValueError("邮箱已被注册")
            
            # 检查用户名是否已存在
            existing_username = await self.get_user_by_username(user_data.username)
            if existing_username:
                raise ValueError("用户名已被使用")
            
            # 加密密码
            password_hash = self.security.hash_password(user_data.password)
            
            # 准备用户数据
            user_id = uuid4()
            now = datetime.utcnow()
            
            user_dict = {
                "id": str(user_id),
                "email": user_data.email,
                "username": user_data.username,
                "full_name": user_data.full_name,
                "avatar_url": user_data.avatar_url,
                "password_hash": password_hash,
                "is_active": True,
                "is_email_verified": False,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }
            
            # 插入数据库
            result = await self.db.insert("users", user_dict)
            if not result:
                raise Exception("用户创建失败")
            
            self.logger.info(f"用户创建成功: {user_data.email}")
            
            # 返回用户信息
            return UserResponse(
                id=user_id,
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                avatar_url=user_data.avatar_url,
                is_active=True,
                is_email_verified=False,
                last_login_at=None,
                created_at=now
            )
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"用户创建失败: {str(e)}")
            raise Exception(f"用户创建失败: {str(e)}")
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[UserResponse]:
        """
        根据用户ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[UserResponse]: 用户信息，不存在则返回None
        """
        try:
            result = await self.db.select(
                "users",
                filters={"id": str(user_id)},
                limit=1
            )
            
            if not result:
                return None
            
            user_data = result[0]
            return self._convert_to_user_response(user_data)
            
        except Exception as e:
            self.logger.error(f"获取用户失败: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """
        根据邮箱获取用户信息
        
        Args:
            email: 邮箱地址
            
        Returns:
            Optional[UserResponse]: 用户信息，不存在则返回None
        """
        try:
            result = await self.db.select(
                "users",
                filters={"email": email},
                limit=1
            )
            
            if not result:
                return None
            
            user_data = result[0]
            return self._convert_to_user_response(user_data)
            
        except Exception as e:
            self.logger.error(f"获取用户失败: {str(e)}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """
        根据用户名获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            Optional[UserResponse]: 用户信息，不存在则返回None
        """
        try:
            result = await self.db.select(
                "users",
                filters={"username": username},
                limit=1
            )
            
            if not result:
                return None
            
            user_data = result[0]
            return self._convert_to_user_response(user_data)
            
        except Exception as e:
            self.logger.error(f"获取用户失败: {str(e)}")
            return None
    
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> Optional[UserResponse]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            user_data: 更新数据
            
        Returns:
            Optional[UserResponse]: 更新后的用户信息
        """
        try:
            # 检查用户是否存在
            existing_user = await self.get_user_by_id(user_id)
            if not existing_user:
                return None
            
            # 准备更新数据
            update_dict = {}
            if user_data.username is not None:
                # 检查用户名是否已被其他用户使用
                existing_username = await self.get_user_by_username(user_data.username)
                if existing_username and existing_username.id != user_id:
                    raise ValueError("用户名已被使用")
                update_dict["username"] = user_data.username
            
            if user_data.full_name is not None:
                update_dict["full_name"] = user_data.full_name
            
            if user_data.avatar_url is not None:
                update_dict["avatar_url"] = user_data.avatar_url
            
            if user_data.is_active is not None:
                update_dict["is_active"] = user_data.is_active
            
            if not update_dict:
                return existing_user
            
            update_dict["updated_at"] = datetime.utcnow().isoformat()
            
            # 更新数据库
            result = await self.db.update(
                "users",
                update_dict,
                filters={"id": str(user_id)}
            )
            
            if not result:
                raise Exception("用户更新失败")
            
            self.logger.info(f"用户更新成功: {user_id}")
            
            # 返回更新后的用户信息
            return await self.get_user_by_id(user_id)
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"用户更新失败: {str(e)}")
            raise Exception(f"用户更新失败: {str(e)}")
    
    async def update_last_login(self, user_id: UUID) -> bool:
        """
        更新用户最后登录时间
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 更新是否成功
        """
        try:
            result = await self.db.update(
                "users",
                {
                    "last_login_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                filters={"id": str(user_id)}
            )
            
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"更新登录时间失败: {str(e)}")
            return False
    
    async def verify_email(self, user_id: UUID) -> bool:
        """
        验证用户邮箱
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 验证是否成功
        """
        try:
            result = await self.db.update(
                "users",
                {
                    "is_email_verified": True,
                    "updated_at": datetime.utcnow().isoformat()
                },
                filters={"id": str(user_id)}
            )
            
            if result:
                self.logger.info(f"邮箱验证成功: {user_id}")
            
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"邮箱验证失败: {str(e)}")
            return False
    
    async def deactivate_user(self, user_id: UUID) -> bool:
        """
        停用用户账户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 停用是否成功
        """
        try:
            result = await self.db.update(
                "users",
                {
                    "is_active": False,
                    "updated_at": datetime.utcnow().isoformat()
                },
                filters={"id": str(user_id)}
            )
            
            if result:
                self.logger.info(f"用户停用成功: {user_id}")
            
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"用户停用失败: {str(e)}")
            return False
    
    async def get_user_stats(self, user_id: UUID) -> Dict[str, Any]:
        """
        获取用户统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict[str, Any]: 用户统计信息
        """
        try:
            # 获取用户基本信息
            user = await self.get_user_by_id(user_id)
            if not user:
                return {}
            
            # 获取聊天会话数量
            sessions_result = await self.db.select(
                "chat_sessions",
                filters={"user_id": str(user_id)},
                count_only=True
            )
            session_count = sessions_result[0].get("count", 0) if sessions_result else 0
            
            # 获取消息数量
            messages_result = await self.db.execute_query(
                """
                SELECT COUNT(*) as count
                FROM chat_messages cm
                JOIN chat_sessions cs ON cm.session_id = cs.id
                WHERE cs.user_id = %s AND cm.message_type = 'user'
                """,
                (str(user_id),)
            )
            message_count = messages_result[0].get("count", 0) if messages_result else 0
            
            return {
                "user_id": str(user_id),
                "username": user.username,
                "email": user.email,
                "session_count": session_count,
                "message_count": message_count,
                "is_active": user.is_active,
                "is_email_verified": user.is_email_verified,
                "created_at": user.created_at,
                "last_login_at": user.last_login_at
            }
            
        except Exception as e:
            self.logger.error(f"获取用户统计失败: {str(e)}")
            return {}
    
    def _convert_to_user_response(self, user_data: Dict[str, Any]) -> UserResponse:
        """
        将数据库数据转换为用户响应模型
        
        Args:
            user_data: 数据库用户数据
            
        Returns:
            UserResponse: 用户响应模型
        """
        return UserResponse(
            id=UUID(user_data["id"]),
            email=user_data["email"],
            username=user_data["username"],
            full_name=user_data.get("full_name"),
            avatar_url=user_data.get("avatar_url"),
            is_active=user_data["is_active"],
            is_email_verified=user_data["is_email_verified"],
            last_login_at=datetime.fromisoformat(user_data["last_login_at"]) if user_data.get("last_login_at") else None,
            created_at=datetime.fromisoformat(user_data["created_at"])
        )