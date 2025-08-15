#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy AI角色数据模型

定义AI角色相关的数据模型:
- AIRole: AI角色基础模型
- AIRoleCreate: AI角色创建模型
- AIRoleUpdate: AI角色更新模型
- AIRoleResponse: AI角色响应模型
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID
from enum import Enum


class AIRoleType(str, Enum):
    """
    AI角色类型枚举
    """
    ASSISTANT = "assistant"  # 智能助手
    CREATIVE = "creative"    # 创意作家
    TECHNICAL = "technical"  # 技术专家
    CASUAL = "casual"        # 轻松聊天


class AIRoleBase(BaseModel):
    """
    AI角色基础模型
    
    包含AI角色的基本信息字段
    """
    name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    description: str = Field(..., min_length=1, max_length=500, description="角色描述")
    role_type: AIRoleType = Field(..., description="角色类型")
    avatar_url: Optional[str] = Field(None, description="角色头像URL")
    personality: str = Field(..., min_length=10, max_length=2000, description="角色性格描述")
    system_prompt: str = Field(..., min_length=10, max_length=5000, description="系统提示词")
    greeting_message: str = Field(..., min_length=1, max_length=500, description="问候语")
    is_active: bool = Field(True, description="是否激活")
    sort_order: int = Field(0, description="排序顺序")
    
    @validator('name')
    def validate_name(cls, v):
        """
        验证角色名称
        
        Args:
            v: 角色名称
            
        Returns:
            str: 验证后的角色名称
            
        Raises:
            ValueError: 角色名称格式不正确
        """
        if not v.strip():
            raise ValueError('角色名称不能为空')
        return v.strip()
    
    @validator('system_prompt')
    def validate_system_prompt(cls, v):
        """
        验证系统提示词
        
        Args:
            v: 系统提示词
            
        Returns:
            str: 验证后的系统提示词
            
        Raises:
            ValueError: 系统提示词格式不正确
        """
        if not v.strip():
            raise ValueError('系统提示词不能为空')
        return v.strip()


class AIRole(AIRoleBase):
    """
    AI角色完整模型
    
    包含数据库中的所有AI角色字段
    """
    id: UUID = Field(..., description="角色ID")
    usage_count: int = Field(0, description="使用次数")
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


class AIRoleCreate(AIRoleBase):
    """
    AI角色创建模型
    
    用于创建新AI角色时的数据验证
    """
    pass


class AIRoleUpdate(BaseModel):
    """
    AI角色更新模型
    
    用于更新AI角色信息
    """
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="角色名称")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="角色描述")
    role_type: Optional[AIRoleType] = Field(None, description="角色类型")
    avatar_url: Optional[str] = Field(None, description="角色头像URL")
    personality: Optional[str] = Field(None, min_length=10, max_length=2000, description="角色性格描述")
    system_prompt: Optional[str] = Field(None, min_length=10, max_length=5000, description="系统提示词")
    greeting_message: Optional[str] = Field(None, min_length=1, max_length=500, description="问候语")
    is_active: Optional[bool] = Field(None, description="是否激活")
    sort_order: Optional[int] = Field(None, description="排序顺序")
    
    @validator('name')
    def validate_name(cls, v):
        """
        验证角色名称
        
        Args:
            v: 角色名称
            
        Returns:
            str: 验证后的角色名称
            
        Raises:
            ValueError: 角色名称格式不正确
        """
        if v is not None and not v.strip():
            raise ValueError('角色名称不能为空')
        return v.strip() if v else v
    
    @validator('system_prompt')
    def validate_system_prompt(cls, v):
        """
        验证系统提示词
        
        Args:
            v: 系统提示词
            
        Returns:
            str: 验证后的系统提示词
            
        Raises:
            ValueError: 系统提示词格式不正确
        """
        if v is not None and not v.strip():
            raise ValueError('系统提示词不能为空')
        return v.strip() if v else v


class AIRoleResponse(BaseModel):
    """
    AI角色响应模型
    
    用于API响应
    """
    id: UUID = Field(..., description="角色ID")
    name: str = Field(..., description="角色名称")
    description: str = Field(..., description="角色描述")
    role_type: AIRoleType = Field(..., description="角色类型")
    avatar_url: Optional[str] = Field(None, description="角色头像URL")
    personality: str = Field(..., description="角色性格描述")
    greeting_message: str = Field(..., description="问候语")
    is_active: bool = Field(..., description="是否激活")
    sort_order: int = Field(..., description="排序顺序")
    usage_count: int = Field(..., description="使用次数")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class AIRoleStats(BaseModel):
    """
    AI角色统计模型
    
    用于角色使用统计
    """
    role_id: UUID = Field(..., description="角色ID")
    role_name: str = Field(..., description="角色名称")
    total_sessions: int = Field(0, description="总会话数")
    total_messages: int = Field(0, description="总消息数")
    avg_session_length: float = Field(0.0, description="平均会话长度")
    last_used_at: Optional[datetime] = Field(None, description="最后使用时间")
    
    class Config:
        """
        Pydantic配置
        """
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }