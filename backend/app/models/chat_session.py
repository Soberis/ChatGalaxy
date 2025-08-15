#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 聊天会话数据模型

定义聊天会话相关的数据模型:
- ChatSession: 聊天会话基础模型
- ChatSessionCreate: 聊天会话创建模型
- ChatSessionUpdate: 聊天会话更新模型
- ChatSessionResponse: 聊天会话响应模型
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from uuid import UUID
from enum import Enum


class SessionStatus(str, Enum):
    """
    会话状态枚举
    """
    ACTIVE = "active"      # 活跃中
    INACTIVE = "inactive"  # 非活跃
    ARCHIVED = "archived"  # 已归档
    DELETED = "deleted"    # 已删除


class ChatSessionBase(BaseModel):
    """
    聊天会话基础模型
    
    包含聊天会话的基本信息字段
    """
    title: str = Field(..., min_length=1, max_length=200, description="会话标题")
    role_id: UUID = Field(..., description="AI角色ID")
    user_id: Optional[UUID] = Field(None, description="用户ID，访客为空")
    is_active: bool = Field(True, description="是否活跃")
    status: SessionStatus = Field(SessionStatus.ACTIVE, description="会话状态")
    
    @validator('title')
    def validate_title(cls, v):
        """
        验证会话标题
        
        Args:
            v: 会话标题
            
        Returns:
            str: 验证后的会话标题
            
        Raises:
            ValueError: 会话标题格式不正确
        """
        if not v.strip():
            raise ValueError('会话标题不能为空')
        return v.strip()


class ChatSession(ChatSessionBase):
    """
    聊天会话完整模型
    
    包含数据库中的所有聊天会话字段
    """
    id: UUID = Field(..., description="会话ID")
    session_token: Optional[str] = Field(None, description="会话令牌（访客用）")
    message_count: int = Field(0, description="消息数量")
    total_tokens: int = Field(0, description="总token数")
    last_message_at: Optional[datetime] = Field(None, description="最后消息时间")
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


class ChatSessionCreate(ChatSessionBase):
    """
    聊天会话创建模型
    
    用于创建新聊天会话时的数据验证
    """
    session_token: Optional[str] = Field(None, description="会话令牌（访客用）")
    
    @validator('session_token')
    def validate_session_token(cls, v, values):
        """
        验证会话令牌
        
        Args:
            v: 会话令牌
            values: 其他字段值
            
        Returns:
            str: 验证后的会话令牌
            
        Raises:
            ValueError: 会话令牌格式不正确
        """
        # 如果没有用户ID，则必须有会话令牌（访客模式）
        if not values.get('user_id') and not v:
            raise ValueError('访客模式下必须提供会话令牌')
        return v


class ChatSessionUpdate(BaseModel):
    """
    聊天会话更新模型
    
    用于更新聊天会话信息
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="会话标题")
    is_active: Optional[bool] = Field(None, description="是否活跃")
    status: Optional[SessionStatus] = Field(None, description="会话状态")
    
    @validator('title')
    def validate_title(cls, v):
        """
        验证会话标题
        
        Args:
            v: 会话标题
            
        Returns:
            str: 验证后的会话标题
            
        Raises:
            ValueError: 会话标题格式不正确
        """
        if v is not None and not v.strip():
            raise ValueError('会话标题不能为空')
        return v.strip() if v else v


class ChatSessionResponse(BaseModel):
    """
    聊天会话响应模型
    
    用于API响应
    """
    id: UUID = Field(..., description="会话ID")
    title: str = Field(..., description="会话标题")
    role_id: UUID = Field(..., description="AI角色ID")
    user_id: Optional[UUID] = Field(None, description="用户ID")
    is_active: bool = Field(..., description="是否活跃")
    status: SessionStatus = Field(..., description="会话状态")
    message_count: int = Field(..., description="消息数量")
    total_tokens: int = Field(..., description="总token数")
    last_message_at: Optional[datetime] = Field(None, description="最后消息时间")
    created_at: datetime = Field(..., description="创建时间")
    
    # 关联数据
    role_name: Optional[str] = Field(None, description="AI角色名称")
    role_avatar: Optional[str] = Field(None, description="AI角色头像")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ChatSessionList(BaseModel):
    """
    聊天会话列表模型
    
    用于分页查询响应
    """
    sessions: List[ChatSessionResponse] = Field(..., description="会话列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


class ChatSessionStats(BaseModel):
    """
    聊天会话统计模型
    
    用于会话统计信息
    """
    total_sessions: int = Field(0, description="总会话数")
    active_sessions: int = Field(0, description="活跃会话数")
    total_messages: int = Field(0, description="总消息数")
    total_tokens: int = Field(0, description="总token数")
    avg_messages_per_session: float = Field(0.0, description="平均每会话消息数")
    most_used_role: Optional[str] = Field(None, description="最常用角色")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True