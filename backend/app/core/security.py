#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 安全认证模块

提供应用的安全功能:
- JWT令牌生成和验证
- 密码加密和验证
- 用户认证中间件
- 权限验证装饰器
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from .config import settings


class SecurityManager:
    """
    安全管理器
    
    负责处理JWT令牌、密码加密等安全相关功能
    """
    
    def __init__(self):
        """
        初始化安全管理器
        """
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建访问令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            str: JWT访问令牌
        """
        to_encode = data.copy()
        
        # 设置过期时间
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        # 生成JWT令牌
        encoded_jwt = jwt.encode(
            to_encode, 
            self.secret_key, 
            algorithm=self.algorithm
        )
        
        logger.debug(f"🔐 创建访问令牌: 用户={data.get('sub')}, 过期时间={expire}")
        return encoded_jwt
    
    def create_refresh_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建刷新令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            str: JWT刷新令牌
        """
        to_encode = data.copy()
        
        # 设置过期时间
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        # 生成JWT令牌
        encoded_jwt = jwt.encode(
            to_encode, 
            self.secret_key, 
            algorithm=self.algorithm
        )
        
        logger.debug(f"🔐 创建刷新令牌: 用户={data.get('sub')}, 过期时间={expire}")
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌
            token_type: 令牌类型 (access/refresh)
            
        Returns:
            Dict[str, Any]: 解码后的令牌数据
            
        Raises:
            HTTPException: 令牌无效或过期
        """
        try:
            # 解码JWT令牌
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # 验证令牌类型
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"无效的令牌类型: 期望{token_type}, 实际{payload.get('type')}",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # 验证过期时间
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="令牌已过期",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            logger.debug(f"🔓 令牌验证成功: 用户={payload.get('sub')}, 类型={token_type}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("⚠️ JWT令牌已过期")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌已过期",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.JWTError as e:
            logger.warning(f"⚠️ JWT令牌验证失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def hash_password(self, password: str) -> str:
        """
        加密密码
        
        Args:
            password: 明文密码
            
        Returns:
            str: 加密后的密码哈希
        """
        # 生成盐值并加密密码
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        logger.debug("🔒 密码加密完成")
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        Args:
            plain_password: 明文密码
            hashed_password: 加密后的密码哈希
            
        Returns:
            bool: 密码是否匹配
        """
        try:
            # 验证密码
            result = bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
            
            logger.debug(f"🔓 密码验证结果: {'成功' if result else '失败'}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 密码验证异常: {str(e)}")
            return False
    
    def create_token_pair(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        创建令牌对(访问令牌+刷新令牌)
        
        Args:
            user_data: 用户数据
            
        Returns:
            Dict[str, str]: 包含访问令牌和刷新令牌的字典
        """
        access_token = self.create_access_token(user_data)
        refresh_token = self.create_refresh_token(user_data)
        
        logger.info(f"🎫 创建令牌对: 用户={user_data.get('sub')}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }


# 全局安全管理器实例
security_manager = SecurityManager()

# HTTP Bearer认证方案
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Optional[Dict[str, Any]]:
    """
    获取当前用户信息(可选认证)
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        Optional[Dict[str, Any]]: 用户信息或None
    """
    if not credentials:
        return None
    
    try:
        # 验证访问令牌
        payload = security_manager.verify_token(credentials.credentials, "access")
        return payload
    except HTTPException:
        return None


async def get_current_user_required(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> Dict[str, Any]:
    """
    获取当前用户信息(必需认证)
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        Dict[str, Any]: 用户信息
        
    Raises:
        HTTPException: 认证失败
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证令牌",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 验证访问令牌
    payload = security_manager.verify_token(credentials.credentials, "access")
    return payload


async def get_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user_required)
) -> Dict[str, Any]:
    """
    获取管理员用户信息
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        Dict[str, Any]: 管理员用户信息
        
    Raises:
        HTTPException: 权限不足
    """
    user_role = current_user.get("role", "user")
    
    if user_role != "admin":
        logger.warning(f"⚠️ 权限不足: 用户={current_user.get('sub')}, 角色={user_role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    
    return current_user


def require_permissions(*required_permissions: str):
    """
    权限验证装饰器
    
    Args:
        *required_permissions: 需要的权限列表
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        async def wrapper(
            current_user: Dict[str, Any] = Depends(get_current_user_required),
            *args, 
            **kwargs
        ):
            user_permissions = current_user.get("permissions", [])
            
            # 检查权限
            for permission in required_permissions:
                if permission not in user_permissions:
                    logger.warning(
                        f"⚠️ 权限不足: 用户={current_user.get('sub')}, "
                        f"需要权限={permission}, 拥有权限={user_permissions}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"权限不足，需要权限: {permission}"
                    )
            
            return await func(current_user=current_user, *args, **kwargs)
        
        return wrapper
    return decorator


async def verify_refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> Dict[str, Any]:
    """
    验证刷新令牌
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        Dict[str, Any]: 令牌载荷
        
    Raises:
        HTTPException: 令牌无效
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少刷新令牌",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 验证刷新令牌
    payload = security_manager.verify_token(credentials.credentials, "refresh")
    return payload


def create_api_key(user_id: str, name: str) -> str:
    """
    创建API密钥
    
    Args:
        user_id: 用户ID
        name: API密钥名称
        
    Returns:
        str: API密钥
    """
    import secrets
    
    # 生成随机API密钥
    api_key = f"cgx_{secrets.token_urlsafe(32)}"
    
    logger.info(f"🔑 创建API密钥: 用户={user_id}, 名称={name}")
    return api_key


def hash_api_key(api_key: str) -> str:
    """
    对API密钥进行哈希处理
    
    Args:
        api_key: API密钥
        
    Returns:
        str: 哈希后的API密钥
    """
    return api_key  # 暂时返回原密钥，后续可以添加哈希处理


if __name__ == "__main__":
    """
    测试安全功能
    """
    # 创建安全管理器
    sm = SecurityManager()
    
    # 测试密码加密和验证
    password = "test_password_123"
    hashed = sm.hash_password(password)
    print(f"原密码: {password}")
    print(f"加密后: {hashed}")
    print(f"验证结果: {sm.verify_password(password, hashed)}")
    print(f"错误密码验证: {sm.verify_password('wrong_password', hashed)}")
    
    # 测试JWT令牌
    user_data = {"sub": "user123", "email": "test@example.com", "role": "user"}
    tokens = sm.create_token_pair(user_data)
    print(f"\n访问令牌: {tokens['access_token'][:50]}...")
    print(f"刷新令牌: {tokens['refresh_token'][:50]}...")
    
    # 验证令牌
    try:
        payload = sm.verify_token(tokens['access_token'], "access")
        print(f"\n令牌验证成功: {payload}")
    except Exception as e:
        print(f"令牌验证失败: {e}")
    
    # 测试API密钥
    api_key = create_api_key("user123", "测试密钥")
    hashed_key = hash_api_key(api_key)
    print(f"\nAPI密钥: {api_key}")
    print(f"哈希后: {hashed_key}")
    
    print("\n✅ 安全功能测试完成")