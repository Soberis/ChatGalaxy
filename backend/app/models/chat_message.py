#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 聊天消息数据模型

定义聊天消息相关的数据模型:
- ChatMessage: 聊天消息基础模型
- ChatMessageCreate: 聊天消息创建模型
- ChatMessageUpdate: 聊天消息更新模型
- ChatMessageResponse: 聊天消息响应模型
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from uuid import UUID
from enum import Enum


class MessageType(str, Enum):
    """
    消息类型枚举
    """
    USER = "user"          # 用户消息
    ASSISTANT = "assistant" # AI助手消息
    SYSTEM = "system"      # 系统消息
    ERROR = "error"        # 错误消息


class MessageStatus(str, Enum):
    """
    消息状态枚举
    """
    PENDING = "pending"     # 待处理
    PROCESSING = "processing" # 处理中
    COMPLETED = "completed" # 已完成
    FAILED = "failed"      # 失败
    DELETED = "deleted"    # 已删除


class ChatMessageBase(BaseModel):
    """
    聊天消息基础模型
    
    包含聊天消息的基本信息字段
    """
    session_id: UUID = Field(..., description="会话ID")
    content: str = Field(..., min_length=1, max_length=10000, description="消息内容")
    message_type: MessageType = Field(..., description="消息类型")
    role_id: Optional[UUID] = Field(None, description="AI角色ID")
    
    @validator('content')
    def validate_content(cls, v):
        """
        验证消息内容
        
        Args:
            v: 消息内容
            
        Returns:
            str: 验证后的消息内容
            
        Raises:
            ValueError: 消息内容格式不正确
        """
        if not v.strip():
            raise ValueError('消息内容不能为空')
        return v.strip()


class ChatMessage(ChatMessageBase):
    """
    聊天消息完整模型
    
    包含数据库中的所有聊天消息字段
    """
    id: UUID = Field(..., description="消息ID")
    parent_id: Optional[UUID] = Field(None, description="父消息ID")
    status: MessageStatus = Field(MessageStatus.COMPLETED, description="消息状态")
    tokens_used: int = Field(0, description="使用的token数")
    metadata: Optional[Dict[str, Any]] = Field(None, description="消息元数据")
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


class ChatMessageCreate(ChatMessageBase):
    """
    聊天消息创建模型
    
    用于创建新聊天消息时的数据验证
    """
    parent_id: Optional[UUID] = Field(None, description="父消息ID")
    status: MessageStatus = Field(MessageStatus.PENDING, description="消息状态")
    metadata: Optional[Dict[str, Any]] = Field(None, description="消息元数据")
    
    @validator('metadata')
    def validate_metadata(cls, v):
        """
        验证消息元数据
        
        Args:
            v: 消息元数据
            
        Returns:
            Dict[str, Any]: 验证后的元数据
        """
        if v is not None:
            # 限制元数据大小
            import json
            if len(json.dumps(v)) > 5000:  # 5KB限制
                raise ValueError('消息元数据过大，最大5KB')
        return v


class ChatMessageUpdate(BaseModel):
    """
    聊天消息更新模型
    
    用于更新聊天消息信息
    """
    content: Optional[str] = Field(None, min_length=1, max_length=10000, description="消息内容")
    status: Optional[MessageStatus] = Field(None, description="消息状态")
    tokens_used: Optional[int] = Field(None, ge=0, description="使用的token数")
    metadata: Optional[Dict[str, Any]] = Field(None, description="消息元数据")
    
    @validator('content')
    def validate_content(cls, v):
        """
        验证消息内容
        
        Args:
            v: 消息内容
            
        Returns:
            str: 验证后的消息内容
            
        Raises:
            ValueError: 消息内容格式不正确
        """
        if v is not None and not v.strip():
            raise ValueError('消息内容不能为空')
        return v.strip() if v else v
    
    @validator('metadata')
    def validate_metadata(cls, v):
        """
        验证消息元数据
        
        Args:
            v: 消息元数据
            
        Returns:
            Dict[str, Any]: 验证后的元数据
        """
        if v is not None:
            # 限制元数据大小
            import json
            if len(json.dumps(v)) > 5000:  # 5KB限制
                raise ValueError('消息元数据过大，最大5KB')
        return v


class ChatMessageResponse(BaseModel):
    """
    聊天消息响应模型
    
    用于API响应
    """
    id: UUID = Field(..., description="消息ID")
    session_id: UUID = Field(..., description="会话ID")
    parent_id: Optional[UUID] = Field(None, description="父消息ID")
    content: str = Field(..., description="消息内容")
    message_type: MessageType = Field(..., description="消息类型")
    role_id: Optional[UUID] = Field(None, description="AI角色ID")
    status: MessageStatus = Field(..., description="消息状态")
    tokens_used: int = Field(..., description="使用的token数")
    metadata: Optional[Dict[str, Any]] = Field(None, description="消息元数据")
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


class ChatMessageList(BaseModel):
    """
    聊天消息列表模型
    
    用于分页查询响应
    """
    messages: List[ChatMessageResponse] = Field(..., description="消息列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


class MessageThread(BaseModel):
    """
    消息线程模型
    
    用于表示消息的对话线程
    """
    parent_message: Optional[ChatMessageResponse] = Field(None, description="父消息")
    replies: List[ChatMessageResponse] = Field([], description="回复消息列表")
    total_replies: int = Field(0, description="总回复数")


class MessageStats(BaseModel):
    """
    消息统计模型
    
    用于消息统计信息
    """
    total_messages: int = Field(0, description="总消息数")
    user_messages: int = Field(0, description="用户消息数")
    assistant_messages: int = Field(0, description="AI消息数")
    system_messages: int = Field(0, description="系统消息数")
    total_tokens: int = Field(0, description="总token数")
    avg_tokens_per_message: float = Field(0.0, description="平均每消息token数")
    avg_message_length: float = Field(0.0, description="平均消息长度")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True