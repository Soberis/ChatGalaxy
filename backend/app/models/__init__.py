#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 数据模型模块

定义应用程序的所有数据模型:
- User: 用户模型
- AIRole: AI角色模型
- ChatSession: 聊天会话模型
- ChatMessage: 聊天消息模型
- Auth: 认证相关模型
- Chat: 聊天相关模型
"""

# 导入用户相关模型
from .user import (
    User, UserBase, UserCreate, UserUpdate, UserResponse
)

# 导入AI角色相关模型
from .ai_role import (
    AIRole, AIRoleBase, AIRoleCreate, AIRoleUpdate, AIRoleResponse,
    AIRoleStats, AIRoleType
)

# 导入聊天会话相关模型
from .chat_session import (
    ChatSession, ChatSessionBase, ChatSessionCreate, ChatSessionUpdate,
    ChatSessionResponse, ChatSessionList, ChatSessionStats, SessionStatus
)

# 导入聊天消息相关模型
from .chat_message import (
    ChatMessage, ChatMessageBase, ChatMessageCreate, ChatMessageUpdate,
    ChatMessageResponse, ChatMessageList, MessageThread, MessageStats,
    MessageType, MessageStatus
)

# 导入认证相关模型
from .auth import (
    LoginRequest, RegisterRequest, TokenResponse, RefreshTokenRequest,
    PasswordResetRequest, PasswordResetConfirm, EmailVerificationRequest,
    EmailVerificationConfirm, ChangePasswordRequest, LoginResponse,
    RegisterResponse, LogoutResponse
)

# 导入聊天相关模型
from .chat import (
    ChatRequest, StreamChatResponse, ChatResponse, ChatHistory,
    ChatContext, ChatSessionCreate as ChatSessionCreateRequest,
    ChatSessionResponse as ChatSessionResponseModel, ChatError,
    ChatStats, ChatMode
)


# 导出所有模型
__all__ = [
    # 用户模型
    "User", "UserBase", "UserCreate", "UserUpdate", "UserResponse",
    
    # AI角色模型
    "AIRole", "AIRoleBase", "AIRoleCreate", "AIRoleUpdate", "AIRoleResponse",
    "AIRoleStats", "AIRoleType",
    
    # 聊天会话模型
    "ChatSession", "ChatSessionBase", "ChatSessionCreate", "ChatSessionUpdate", 
    "ChatSessionResponse", "ChatSessionList", "ChatSessionStats", "SessionStatus",
    
    # 聊天消息模型
    "ChatMessage", "ChatMessageBase", "ChatMessageCreate", "ChatMessageUpdate", 
    "ChatMessageResponse", "ChatMessageList", "MessageThread", "MessageStats",
    "MessageType", "MessageStatus",
    
    # 认证模型
    "LoginRequest", "RegisterRequest", "TokenResponse", "RefreshTokenRequest",
    "PasswordResetRequest", "PasswordResetConfirm", "EmailVerificationRequest",
    "EmailVerificationConfirm", "ChangePasswordRequest", "LoginResponse",
    "RegisterResponse", "LogoutResponse",
    
    # 聊天模型
    "ChatRequest", "StreamChatResponse", "ChatResponse", "ChatHistory",
    "ChatContext", "ChatSessionCreateRequest", "ChatSessionResponseModel",
    "ChatError", "ChatStats", "ChatMode",
]