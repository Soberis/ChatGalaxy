#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 认证数据模型

定义用户认证相关的数据模型:
- LoginRequest: 登录请求模型
- RegisterRequest: 注册请求模型
- TokenResponse: 令牌响应模型
- RefreshTokenRequest: 刷新令牌请求模型
- PasswordResetRequest: 密码重置请求模型
- EmailVerificationRequest: 邮箱验证请求模型
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
from uuid import UUID


class LoginRequest(BaseModel):
    """
    登录请求模型
    
    用于用户登录验证
    """
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    remember_me: bool = Field(False, description="记住我")
    
    @validator('password')
    def validate_password(cls, v):
        """
        验证密码格式
        
        Args:
            v: 密码
            
        Returns:
            str: 验证后的密码
            
        Raises:
            ValueError: 密码格式不正确
        """
        if len(v.strip()) < 6:
            raise ValueError('密码长度不能少于6位')
        return v.strip()


class RegisterRequest(BaseModel):
    """
    注册请求模型
    
    用于用户注册验证
    """
    email: EmailStr = Field(..., description="邮箱地址")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    confirm_password: str = Field(..., min_length=6, max_length=128, description="确认密码")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    
    @validator('username')
    def validate_username(cls, v):
        """
        验证用户名格式
        
        Args:
            v: 用户名
            
        Returns:
            str: 验证后的用户名
            
        Raises:
            ValueError: 用户名格式不正确
        """
        import re
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线和中文字符')
        if len(v) < 3:
            raise ValueError('用户名长度不能少于3位')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """
        验证密码强度
        
        Args:
            v: 密码
            
        Returns:
            str: 验证后的密码
            
        Raises:
            ValueError: 密码强度不够
        """
        import re
        v = v.strip()
        if len(v) < 6:
            raise ValueError('密码长度不能少于6位')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        """
        验证确认密码
        
        Args:
            v: 确认密码
            values: 其他字段值
            
        Returns:
            str: 验证后的确认密码
            
        Raises:
            ValueError: 确认密码不匹配
        """
        if 'password' in values and v != values['password']:
            raise ValueError('确认密码与密码不匹配')
        return v


class TokenResponse(BaseModel):
    """
    令牌响应模型
    
    用于返回认证令牌信息
    """
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")
    user_id: UUID = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱地址")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    """
    刷新令牌请求模型
    
    用于刷新访问令牌
    """
    refresh_token: str = Field(..., description="刷新令牌")
    
    @validator('refresh_token')
    def validate_refresh_token(cls, v):
        """
        验证刷新令牌格式
        
        Args:
            v: 刷新令牌
            
        Returns:
            str: 验证后的刷新令牌
            
        Raises:
            ValueError: 刷新令牌格式不正确
        """
        if not v.strip():
            raise ValueError('刷新令牌不能为空')
        return v.strip()


class PasswordResetRequest(BaseModel):
    """
    密码重置请求模型
    
    用于请求密码重置
    """
    email: EmailStr = Field(..., description="邮箱地址")


class PasswordResetConfirm(BaseModel):
    """
    密码重置确认模型
    
    用于确认密码重置
    """
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=6, max_length=128, description="新密码")
    confirm_password: str = Field(..., min_length=6, max_length=128, description="确认新密码")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """
        验证新密码强度
        
        Args:
            v: 新密码
            
        Returns:
            str: 验证后的新密码
            
        Raises:
            ValueError: 新密码强度不够
        """
        import re
        v = v.strip()
        if len(v) < 6:
            raise ValueError('密码长度不能少于6位')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        """
        验证确认新密码
        
        Args:
            v: 确认新密码
            values: 其他字段值
            
        Returns:
            str: 验证后的确认新密码
            
        Raises:
            ValueError: 确认新密码不匹配
        """
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('确认密码与新密码不匹配')
        return v


class EmailVerificationRequest(BaseModel):
    """
    邮箱验证请求模型
    
    用于请求邮箱验证
    """
    email: EmailStr = Field(..., description="邮箱地址")


class EmailVerificationConfirm(BaseModel):
    """
    邮箱验证确认模型
    
    用于确认邮箱验证
    """
    token: str = Field(..., description="验证令牌")
    
    @validator('token')
    def validate_token(cls, v):
        """
        验证令牌格式
        
        Args:
            v: 验证令牌
            
        Returns:
            str: 验证后的令牌
            
        Raises:
            ValueError: 令牌格式不正确
        """
        if not v.strip():
            raise ValueError('验证令牌不能为空')
        return v.strip()


class ChangePasswordRequest(BaseModel):
    """
    修改密码请求模型
    
    用于用户修改密码
    """
    current_password: str = Field(..., min_length=6, max_length=128, description="当前密码")
    new_password: str = Field(..., min_length=6, max_length=128, description="新密码")
    confirm_password: str = Field(..., min_length=6, max_length=128, description="确认新密码")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """
        验证新密码强度
        
        Args:
            v: 新密码
            
        Returns:
            str: 验证后的新密码
            
        Raises:
            ValueError: 新密码强度不够
        """
        import re
        v = v.strip()
        if len(v) < 6:
            raise ValueError('密码长度不能少于6位')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        """
        验证确认新密码
        
        Args:
            v: 确认新密码
            values: 其他字段值
            
        Returns:
            str: 验证后的确认新密码
            
        Raises:
            ValueError: 确认新密码不匹配
        """
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('确认密码与新密码不匹配')
        return v


class LoginResponse(BaseModel):
    """
    登录响应模型
    
    用于返回登录结果
    """
    success: bool = Field(..., description="登录是否成功")
    message: str = Field(..., description="响应消息")
    token: Optional[TokenResponse] = Field(None, description="令牌信息")
    user: Optional[dict] = Field(None, description="用户信息")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True


class RegisterResponse(BaseModel):
    """
    注册响应模型
    
    用于返回注册结果
    """
    success: bool = Field(..., description="注册是否成功")
    message: str = Field(..., description="响应消息")
    user_id: Optional[UUID] = Field(None, description="用户ID")
    email_verification_required: bool = Field(True, description="是否需要邮箱验证")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True


class LogoutResponse(BaseModel):
    """
    登出响应模型
    
    用于返回登出结果
    """
    success: bool = Field(..., description="登出是否成功")
    message: str = Field(..., description="响应消息")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True