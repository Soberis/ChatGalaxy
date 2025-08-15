#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 服务模块

定义应用程序的所有业务逻辑服务:
- UserService: 用户管理服务
- AIRoleService: AI角色管理服务
- ChatService: 聊天服务
- AuthService: 认证服务
- WebSocketService: WebSocket服务
"""

# 导入用户服务
from .user_service import UserService

# 导入AI角色服务
from .ai_role_service import AIRoleService

# 导入聊天服务
from .chat_service import ChatService

# 导入认证服务
from .auth_service import AuthService

# 导入WebSocket服务
from .websocket_service import WebSocketService, WebSocketConnection, ConnectionType, MessageType


# 导出所有服务
__all__ = [
    "UserService",
    "AIRoleService", 
    "ChatService",
    "AuthService",
    "WebSocketService",
    "WebSocketConnection",
    "ConnectionType",
    "MessageType",
]