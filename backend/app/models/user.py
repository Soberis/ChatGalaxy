#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 用户数据模型

定义用户相关的数据模型:
- User: 用户基础模型
- UserCreate: 用户创建模型
- UserUpdate: 用户更新模型
- UserResponse: 用户响应模型
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID


class UserBase(BaseModel):
    """
    用户基础模型
    
    包含用户的基本信息字段
    """
    email: EmailStr = Field(..., description="用户邮箱")
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    full_name: Optional[str] = Field(None, max_length=100, description="用户全名")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    is_active: bool = Field(True, description="是否激活")
    
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
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v


class User(UserBase):
    """
    用户完整模型
    
    包含数据库中的所有用户字段
    """
    id: UUID = Field(..., description="用户ID")
    password_hash: str = Field(..., description="密码哈希")
    email_verified: bool = Field(False, description="邮箱是否已验证")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class UserCreate(UserBase):
    """
    用户创建模型
    
    用于用户注册时的数据验证
    """
    password: str = Field(..., min_length=8, max_length=128, description="用户密码")
    confirm_password: str = Field(..., description="确认密码")
    
    @validator('password')
    def validate_password(cls, v):
        """
        验证密码强度
        
        Args:
            v: 密码
            
        Returns:
            str: 验证后的密码
            
        Raises:
            ValueError: 密码不符合要求
        """
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        
        # 检查是否包含字母和数字
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_letter and has_digit):
            raise ValueError('密码必须包含字母和数字')
        
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
            ValueError: 两次密码不一致
        """
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v


class UserUpdate(BaseModel):
    """
    用户更新模型
    
    用于更新用户信息
    """
    username: Optional[str] = Field(None, min_length=2, max_length=50, description="用户名")
    full_name: Optional[str] = Field(None, max_length=100, description="用户全名")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    is_active: Optional[bool] = Field(None, description="是否激活")
    
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
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v


class UserResponse(BaseModel):
    """
    用户响应模型
    
    用于API响应，不包含敏感信息
    """
    id: UUID = Field(..., description="用户ID")
    email: EmailStr = Field(..., description="用户邮箱")
    username: str = Field(..., description="用户名")
    full_name: Optional[str] = Field(None, description="用户全名")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    is_active: bool = Field(..., description="是否激活")
    email_verified: bool = Field(..., description="邮箱是否已验证")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }