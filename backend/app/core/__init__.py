#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 核心模块

提供应用的核心功能:
- 配置管理 (config)
- 数据库连接 (database)
- 日志系统 (logging)
- 安全认证 (security)

使用示例:
    from app.core import settings, get_db_client, setup_logging, security_manager
    from app.core.security import get_current_user, get_admin_user
"""

from .config import settings, get_settings
from .database import DatabaseManager, get_db_client, db_manager
from .logging import setup_logging, get_logger
from .security import (
    SecurityManager,
    security_manager,
    get_current_user,
    get_current_user_required,
    get_admin_user,
    verify_refresh_token,
    require_permissions,
    create_api_key,
    hash_api_key
)
from .ai_client import (
    AIClient,
    AIProvider,
    AIMessage,
    AIResponse,
    StreamChunk,
    get_ai_client,
    close_ai_client
)

__all__ = [
    # 配置管理
    "settings",
    "get_settings",
    
    # 数据库
    "DatabaseManager",
    "get_db_client",
    "db_manager",
    
    # 日志系统
    "setup_logging",
    "get_logger",
    
    # 安全认证
    "SecurityManager",
    "security_manager",
    "get_current_user",
    "get_current_user_required",
    "get_admin_user",
    "verify_refresh_token",
    "require_permissions",
    "create_api_key",
    "hash_api_key",
    
    # AI客户端
    "AIClient",
    "AIProvider",
    "AIMessage",
    "AIResponse",
    "StreamChunk",
    "get_ai_client",
    "close_ai_client",
]

# 版本信息
__version__ = "1.0.0"
__author__ = "ChatGalaxy Team"
__description__ = "ChatGalaxy AI聊天平台核心模块"