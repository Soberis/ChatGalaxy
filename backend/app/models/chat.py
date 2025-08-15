#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 聊天数据模型

定义聊天相关的数据模型:
- ChatRequest: 聊天请求模型
- StreamChatResponse: 流式聊天响应模型
- ChatResponse: 聊天响应模型
- ChatHistory: 聊天历史模型
- ChatContext: 聊天上下文模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID
from enum import Enum


class ChatMode(str, Enum):
    """
    聊天模式枚举
    """
    NORMAL = "normal"      # 普通模式
    STREAM = "stream"      # 流式模式
    CONTEXT = "context"    # 上下文模式


class ChatRequest(BaseModel):
    """
    聊天请求模型
    
    用于发送聊天消息
    """
    session_id: Optional[UUID] = Field(None, description="会话ID")
    role_id: UUID = Field(..., description="AI角色ID")
    message: str = Field(..., min_length=1, max_length=10000, description="用户消息")
    mode: ChatMode = Field(ChatMode.NORMAL, description="聊天模式")
    context_messages: Optional[List[Dict[str, Any]]] = Field(None, description="上下文消息")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: Optional[int] = Field(2000, ge=1, le=4000, description="最大token数")
    
    # 访客模式支持
    guest_token: Optional[str] = Field(None, description="访客令牌")
    
    @validator('message')
    def validate_message(cls, v):
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
    
    @validator('context_messages')
    def validate_context_messages(cls, v):
        """
        验证上下文消息
        
        Args:
            v: 上下文消息列表
            
        Returns:
            List[Dict[str, Any]]: 验证后的上下文消息
            
        Raises:
            ValueError: 上下文消息格式不正确
        """
        if v is not None:
            if len(v) > 20:  # 限制上下文消息数量
                raise ValueError('上下文消息数量不能超过20条')
            for msg in v:
                if not isinstance(msg, dict):
                    raise ValueError('上下文消息必须是字典格式')
                if 'role' not in msg or 'content' not in msg:
                    raise ValueError('上下文消息必须包含role和content字段')
                if msg['role'] not in ['user', 'assistant', 'system']:
                    raise ValueError('上下文消息role必须是user、assistant或system')
        return v


class StreamChatResponse(BaseModel):
    """
    流式聊天响应模型
    
    用于流式返回聊天响应
    """
    session_id: UUID = Field(..., description="会话ID")
    message_id: UUID = Field(..., description="消息ID")
    content: str = Field(..., description="响应内容片段")
    is_complete: bool = Field(False, description="是否完成")
    tokens_used: int = Field(0, description="使用的token数")
    timestamp: datetime = Field(..., description="时间戳")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ChatResponse(BaseModel):
    """
    聊天响应模型
    
    用于返回完整的聊天响应
    """
    session_id: UUID = Field(..., description="会话ID")
    message_id: UUID = Field(..., description="消息ID")
    user_message_id: UUID = Field(..., description="用户消息ID")
    content: str = Field(..., description="AI响应内容")
    role_id: UUID = Field(..., description="AI角色ID")
    role_name: str = Field(..., description="AI角色名称")
    tokens_used: int = Field(0, description="使用的token数")
    response_time: float = Field(0.0, description="响应时间(秒)")
    created_at: datetime = Field(..., description="创建时间")
    
    # 元数据
    metadata: Optional[Dict[str, Any]] = Field(None, description="响应元数据")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ChatHistory(BaseModel):
    """
    聊天历史模型
    
    用于返回聊天历史记录
    """
    session_id: UUID = Field(..., description="会话ID")
    messages: List[Dict[str, Any]] = Field(..., description="消息列表")
    total_messages: int = Field(0, description="总消息数")
    total_tokens: int = Field(0, description="总token数")
    session_title: str = Field(..., description="会话标题")
    role_name: str = Field(..., description="AI角色名称")
    created_at: datetime = Field(..., description="会话创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ChatContext(BaseModel):
    """
    聊天上下文模型
    
    用于管理聊天上下文信息
    """
    session_id: UUID = Field(..., description="会话ID")
    role_id: UUID = Field(..., description="AI角色ID")
    system_prompt: str = Field(..., description="系统提示词")
    context_messages: List[Dict[str, Any]] = Field([], description="上下文消息")
    max_context_length: int = Field(10, description="最大上下文长度")
    total_tokens: int = Field(0, description="上下文总token数")
    
    @validator('context_messages')
    def validate_context_messages(cls, v):
        """
        验证上下文消息
        
        Args:
            v: 上下文消息列表
            
        Returns:
            List[Dict[str, Any]]: 验证后的上下文消息
        """
        for msg in v:
            if not isinstance(msg, dict):
                raise ValueError('上下文消息必须是字典格式')
            if 'role' not in msg or 'content' not in msg:
                raise ValueError('上下文消息必须包含role和content字段')
        return v


class ChatSessionCreate(BaseModel):
    """
    创建聊天会话请求模型
    
    用于创建新的聊天会话
    """
    role_id: UUID = Field(..., description="AI角色ID")
    title: Optional[str] = Field(None, max_length=200, description="会话标题")
    guest_token: Optional[str] = Field(None, description="访客令牌")
    
    @validator('title')
    def validate_title(cls, v):
        """
        验证会话标题
        
        Args:
            v: 会话标题
            
        Returns:
            str: 验证后的会话标题
        """
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if len(v) > 200:
                raise ValueError('会话标题长度不能超过200字符')
        return v


class ChatSessionResponse(BaseModel):
    """
    聊天会话响应模型
    
    用于返回会话信息
    """
    session_id: UUID = Field(..., description="会话ID")
    title: str = Field(..., description="会话标题")
    role_id: UUID = Field(..., description="AI角色ID")
    role_name: str = Field(..., description="AI角色名称")
    role_avatar: Optional[str] = Field(None, description="AI角色头像")
    message_count: int = Field(0, description="消息数量")
    total_tokens: int = Field(0, description="总token数")
    is_active: bool = Field(True, description="是否活跃")
    last_message_at: Optional[datetime] = Field(None, description="最后消息时间")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ChatError(BaseModel):
    """
    聊天错误模型
    
    用于返回聊天错误信息
    """
    error_code: str = Field(..., description="错误代码")
    error_message: str = Field(..., description="错误消息")
    session_id: Optional[UUID] = Field(None, description="会话ID")
    timestamp: datetime = Field(..., description="错误时间")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ChatStats(BaseModel):
    """
    聊天统计模型
    
    用于返回聊天统计信息
    """
    total_sessions: int = Field(0, description="总会话数")
    total_messages: int = Field(0, description="总消息数")
    total_tokens: int = Field(0, description="总token数")
    avg_messages_per_session: float = Field(0.0, description="平均每会话消息数")
    avg_tokens_per_message: float = Field(0.0, description="平均每消息token数")
    most_used_role: Optional[str] = Field(None, description="最常用角色")
    active_sessions: int = Field(0, description="活跃会话数")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True