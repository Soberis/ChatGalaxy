#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 认证服务模块

提供用户认证相关的业务逻辑:
- 用户登录和注册
- JWT令牌管理
- 密码重置和邮箱验证
- 权限验证
"""

from typing import Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta
import logging
import secrets
import hashlib

from ..core.database import DatabaseManager
from ..core.security import SecurityManager
from ..core.config import get_settings
from ..models.user import UserResponse
from ..models.auth import (
    LoginRequest, RegisterRequest, TokenResponse, RefreshTokenRequest,
    LoginResponse, RegisterResponse, PasswordResetRequest,
    PasswordResetConfirm, EmailVerificationRequest, EmailVerificationConfirm,
    ChangePasswordRequest
)
from .user_service import UserService


class AuthService:
    """
    认证服务类
    
    提供用户认证和授权的核心业务逻辑
    """
    
    def __init__(self, db: DatabaseManager, security: SecurityManager, user_service: UserService):
        """
        初始化认证服务
        
        Args:
            db: 数据库管理器
            security: 安全管理器
            user_service: 用户服务
        """
        self.db = db
        self.security = security
        self.user_service = user_service
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
    
    async def register(self, register_data: RegisterRequest) -> RegisterResponse:
        """
        用户注册
        
        Args:
            register_data: 注册请求数据
            
        Returns:
            RegisterResponse: 注册响应
            
        Raises:
            ValueError: 注册数据验证失败
            Exception: 注册过程失败
        """
        try:
            # 验证密码一致性
            if register_data.password != register_data.confirm_password:
                raise ValueError("密码和确认密码不一致")
            
            # 创建用户
            from ..models.user import UserCreate
            user_create = UserCreate(
                email=register_data.email,
                username=register_data.username,
                password=register_data.password,
                confirm_password=register_data.confirm_password,
                full_name=register_data.full_name
            )
            
            user = await self.user_service.create_user(user_create)
            
            # 生成邮箱验证令牌
            verification_token = self._generate_verification_token()
            await self._store_verification_token(user.id, verification_token, "email_verification")
            
            self.logger.info(f"用户注册成功: {register_data.email}")
            
            return RegisterResponse(
                success=True,
                message="注册成功，请检查邮箱进行验证",
                user_id=user.id,
                email=user.email,
                username=user.username,
                verification_token=verification_token
            )
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"用户注册失败: {str(e)}")
            raise Exception(f"注册失败: {str(e)}")
    
    async def login(self, login_data: LoginRequest) -> LoginResponse:
        """
        用户登录
        
        Args:
            login_data: 登录请求数据
            
        Returns:
            LoginResponse: 登录响应
            
        Raises:
            ValueError: 登录凭据无效
            Exception: 登录过程失败
        """
        try:
            # 获取用户信息
            user = await self.user_service.get_user_by_email(login_data.email)
            if not user:
                raise ValueError("邮箱或密码错误")
            
            # 检查用户状态
            if not user.is_active:
                raise ValueError("账户已被停用")
            
            # 获取用户密码哈希
            user_data = await self.db.select(
                "users",
                filters={"email": login_data.email},
                columns=["id", "password_hash"],
                limit=1
            )
            
            if not user_data:
                raise ValueError("邮箱或密码错误")
            
            password_hash = user_data[0]["password_hash"]
            
            # 验证密码
            if not self.security.verify_password(login_data.password, password_hash):
                raise ValueError("邮箱或密码错误")
            
            # 生成令牌
            access_token = self.security.create_access_token(
                data={"sub": str(user.id), "email": user.email, "username": user.username}
            )
            refresh_token = self.security.create_refresh_token(
                data={"sub": str(user.id)}
            )
            
            # 更新最后登录时间
            await self.user_service.update_last_login(user.id)
            
            # 存储刷新令牌
            await self._store_refresh_token(user.id, refresh_token)
            
            self.logger.info(f"用户登录成功: {login_data.email}")
            
            return LoginResponse(
                success=True,
                message="登录成功",
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=self.settings.jwt_access_token_expire_minutes * 60,
                user=user
            )
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"用户登录失败: {str(e)}")
            raise Exception(f"登录失败: {str(e)}")
    
    async def refresh_token(self, refresh_data: RefreshTokenRequest) -> TokenResponse:
        """
        刷新访问令牌
        
        Args:
            refresh_data: 刷新令牌请求
            
        Returns:
            TokenResponse: 新的令牌信息
            
        Raises:
            ValueError: 刷新令牌无效
            Exception: 刷新过程失败
        """
        try:
            # 验证刷新令牌
            payload = self.security.verify_refresh_token(refresh_data.refresh_token)
            if not payload:
                raise ValueError("无效的刷新令牌")
            
            user_id = UUID(payload.get("sub"))
            
            # 检查刷新令牌是否存在且有效
            token_valid = await self._verify_refresh_token(user_id, refresh_data.refresh_token)
            if not token_valid:
                raise ValueError("刷新令牌已失效")
            
            # 获取用户信息
            user = await self.user_service.get_user_by_id(user_id)
            if not user or not user.is_active:
                raise ValueError("用户不存在或已被停用")
            
            # 生成新的访问令牌
            access_token = self.security.create_access_token(
                data={"sub": str(user.id), "email": user.email, "username": user.username}
            )
            
            # 生成新的刷新令牌
            new_refresh_token = self.security.create_refresh_token(
                data={"sub": str(user.id)}
            )
            
            # 更新刷新令牌
            await self._update_refresh_token(user_id, refresh_data.refresh_token, new_refresh_token)
            
            self.logger.info(f"令牌刷新成功: {user.email}")
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=self.settings.jwt_access_token_expire_minutes * 60,
                user_id=user.id,
                username=user.username,
                email=user.email
            )
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"令牌刷新失败: {str(e)}")
            raise Exception(f"令牌刷新失败: {str(e)}")
    
    async def logout(self, user_id: UUID, refresh_token: str) -> bool:
        """
        用户登出
        
        Args:
            user_id: 用户ID
            refresh_token: 刷新令牌
            
        Returns:
            bool: 登出是否成功
        """
        try:
            # 删除刷新令牌
            result = await self.db.delete(
                "refresh_tokens",
                filters={"user_id": str(user_id), "token": refresh_token}
            )
            
            self.logger.info(f"用户登出成功: {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"用户登出失败: {str(e)}")
            return False
    
    async def request_password_reset(self, reset_data: PasswordResetRequest) -> bool:
        """
        请求密码重置
        
        Args:
            reset_data: 密码重置请求
            
        Returns:
            bool: 请求是否成功
        """
        try:
            # 检查用户是否存在
            user = await self.user_service.get_user_by_email(reset_data.email)
            if not user:
                # 为了安全，即使用户不存在也返回成功
                return True
            
            # 生成重置令牌
            reset_token = self._generate_verification_token()
            await self._store_verification_token(user.id, reset_token, "password_reset")
            
            self.logger.info(f"密码重置请求成功: {reset_data.email}")
            return True
            
        except Exception as e:
            self.logger.error(f"密码重置请求失败: {str(e)}")
            return False
    
    async def confirm_password_reset(self, confirm_data: PasswordResetConfirm) -> bool:
        """
        确认密码重置
        
        Args:
            confirm_data: 密码重置确认数据
            
        Returns:
            bool: 重置是否成功
            
        Raises:
            ValueError: 重置令牌无效或密码不一致
        """
        try:
            # 验证密码一致性
            if confirm_data.new_password != confirm_data.confirm_password:
                raise ValueError("密码和确认密码不一致")
            
            # 验证重置令牌
            user_id = await self._verify_verification_token(confirm_data.token, "password_reset")
            if not user_id:
                raise ValueError("无效或已过期的重置令牌")
            
            # 更新密码
            password_hash = self.security.hash_password(confirm_data.new_password)
            result = await self.db.update(
                "users",
                {
                    "password_hash": password_hash,
                    "updated_at": datetime.utcnow().isoformat()
                },
                filters={"id": str(user_id)}
            )
            
            if not result:
                raise Exception("密码更新失败")
            
            # 删除重置令牌
            await self._delete_verification_token(confirm_data.token)
            
            # 删除所有刷新令牌，强制重新登录
            await self.db.delete(
                "refresh_tokens",
                filters={"user_id": str(user_id)}
            )
            
            self.logger.info(f"密码重置成功: {user_id}")
            return True
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"密码重置失败: {str(e)}")
            raise Exception(f"密码重置失败: {str(e)}")
    
    async def verify_email(self, verify_data: EmailVerificationConfirm) -> bool:
        """
        验证邮箱
        
        Args:
            verify_data: 邮箱验证确认数据
            
        Returns:
            bool: 验证是否成功
            
        Raises:
            ValueError: 验证令牌无效
        """
        try:
            # 验证邮箱验证令牌
            user_id = await self._verify_verification_token(verify_data.token, "email_verification")
            if not user_id:
                raise ValueError("无效或已过期的验证令牌")
            
            # 更新邮箱验证状态
            success = await self.user_service.verify_email(user_id)
            if not success:
                raise Exception("邮箱验证更新失败")
            
            # 删除验证令牌
            await self._delete_verification_token(verify_data.token)
            
            self.logger.info(f"邮箱验证成功: {user_id}")
            return True
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"邮箱验证失败: {str(e)}")
            raise Exception(f"邮箱验证失败: {str(e)}")
    
    async def change_password(self, user_id: UUID, change_data: ChangePasswordRequest) -> bool:
        """
        修改密码
        
        Args:
            user_id: 用户ID
            change_data: 修改密码请求
            
        Returns:
            bool: 修改是否成功
            
        Raises:
            ValueError: 密码验证失败
        """
        try:
            # 验证新密码一致性
            if change_data.new_password != change_data.confirm_password:
                raise ValueError("新密码和确认密码不一致")
            
            # 获取当前密码哈希
            user_data = await self.db.select(
                "users",
                filters={"id": str(user_id)},
                columns=["password_hash"],
                limit=1
            )
            
            if not user_data:
                raise ValueError("用户不存在")
            
            current_password_hash = user_data[0]["password_hash"]
            
            # 验证当前密码
            if not self.security.verify_password(change_data.current_password, current_password_hash):
                raise ValueError("当前密码错误")
            
            # 更新密码
            new_password_hash = self.security.hash_password(change_data.new_password)
            result = await self.db.update(
                "users",
                {
                    "password_hash": new_password_hash,
                    "updated_at": datetime.utcnow().isoformat()
                },
                filters={"id": str(user_id)}
            )
            
            if not result:
                raise Exception("密码更新失败")
            
            # 删除所有刷新令牌，强制重新登录
            await self.db.delete(
                "refresh_tokens",
                filters={"user_id": str(user_id)}
            )
            
            self.logger.info(f"密码修改成功: {user_id}")
            return True
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"密码修改失败: {str(e)}")
            raise Exception(f"密码修改失败: {str(e)}")
    
    async def get_current_user(self, token: str) -> Optional[UserResponse]:
        """
        根据访问令牌获取当前用户
        
        Args:
            token: 访问令牌
            
        Returns:
            Optional[UserResponse]: 用户信息，无效则返回None
        """
        try:
            # 验证访问令牌
            payload = self.security.verify_access_token(token)
            if not payload:
                return None
            
            user_id = UUID(payload.get("sub"))
            return await self.user_service.get_user_by_id(user_id)
            
        except Exception as e:
            self.logger.error(f"获取当前用户失败: {str(e)}")
            return None
    
    def _generate_verification_token(self) -> str:
        """
        生成验证令牌
        
        Returns:
            str: 验证令牌
        """
        return secrets.token_urlsafe(32)
    
    async def _store_verification_token(self, user_id: UUID, token: str, token_type: str) -> bool:
        """
        存储验证令牌
        
        Args:
            user_id: 用户ID
            token: 令牌
            token_type: 令牌类型
            
        Returns:
            bool: 存储是否成功
        """
        try:
            expires_at = datetime.utcnow() + timedelta(hours=24)  # 24小时有效期
            
            token_data = {
                "user_id": str(user_id),
                "token": token,
                "token_type": token_type,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = await self.db.insert("verification_tokens", token_data)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"存储验证令牌失败: {str(e)}")
            return False
    
    async def _verify_verification_token(self, token: str, token_type: str) -> Optional[UUID]:
        """
        验证验证令牌
        
        Args:
            token: 令牌
            token_type: 令牌类型
            
        Returns:
            Optional[UUID]: 用户ID，无效则返回None
        """
        try:
            result = await self.db.select(
                "verification_tokens",
                filters={"token": token, "token_type": token_type},
                limit=1
            )
            
            if not result:
                return None
            
            token_data = result[0]
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            
            # 检查是否过期
            if datetime.utcnow() > expires_at:
                # 删除过期令牌
                await self._delete_verification_token(token)
                return None
            
            return UUID(token_data["user_id"])
            
        except Exception as e:
            self.logger.error(f"验证验证令牌失败: {str(e)}")
            return None
    
    async def _delete_verification_token(self, token: str) -> bool:
        """
        删除验证令牌
        
        Args:
            token: 令牌
            
        Returns:
            bool: 删除是否成功
        """
        try:
            result = await self.db.delete(
                "verification_tokens",
                filters={"token": token}
            )
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"删除验证令牌失败: {str(e)}")
            return False
    
    async def _store_refresh_token(self, user_id: UUID, token: str) -> bool:
        """
        存储刷新令牌
        
        Args:
            user_id: 用户ID
            token: 刷新令牌
            
        Returns:
            bool: 存储是否成功
        """
        try:
            expires_at = datetime.utcnow() + timedelta(days=self.settings.jwt_refresh_token_expire_days)
            
            token_data = {
                "user_id": str(user_id),
                "token": token,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = await self.db.insert("refresh_tokens", token_data)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"存储刷新令牌失败: {str(e)}")
            return False
    
    async def _verify_refresh_token(self, user_id: UUID, token: str) -> bool:
        """
        验证刷新令牌
        
        Args:
            user_id: 用户ID
            token: 刷新令牌
            
        Returns:
            bool: 令牌是否有效
        """
        try:
            result = await self.db.select(
                "refresh_tokens",
                filters={"user_id": str(user_id), "token": token},
                limit=1
            )
            
            if not result:
                return False
            
            token_data = result[0]
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            
            # 检查是否过期
            if datetime.utcnow() > expires_at:
                # 删除过期令牌
                await self.db.delete(
                    "refresh_tokens",
                    filters={"token": token}
                )
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证刷新令牌失败: {str(e)}")
            return False
    
    async def _update_refresh_token(self, user_id: UUID, old_token: str, new_token: str) -> bool:
        """
        更新刷新令牌
        
        Args:
            user_id: 用户ID
            old_token: 旧令牌
            new_token: 新令牌
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 删除旧令牌
            await self.db.delete(
                "refresh_tokens",
                filters={"user_id": str(user_id), "token": old_token}
            )
            
            # 存储新令牌
            return await self._store_refresh_token(user_id, new_token)
            
        except Exception as e:
            self.logger.error(f"更新刷新令牌失败: {str(e)}")
            return False