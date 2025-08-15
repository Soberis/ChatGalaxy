#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 配置管理模块

管理应用程序的所有配置项:
- 数据库配置
- JWT认证配置
- AI服务配置
- 邮件服务配置
- 应用程序设置
"""

import os
from typing import Optional, List
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """
    应用程序配置类
    
    使用Pydantic进行配置验证和类型检查
    """
    
    # 应用程序基础配置
    APP_NAME: str = "ChatGalaxy"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI智能聊天平台"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    
    # 跨域配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://chatgalaxy.vercel.app"
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Supabase数据库配置
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # PostgreSQL数据库配置（备用）
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "chatgalaxy"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "root"
    
    # JWT认证配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 密码加密配置
    PASSWORD_HASH_ALGORITHM: str = "argon2"
    PASSWORD_HASH_ROUNDS: int = 12
    
    # AI服务配置
    # 阿里通义千问
    QWEN_API_KEY: str
    QWEN_MODEL: str = "qwen-turbo"
    QWEN_MAX_TOKENS: int = 2000
    QWEN_TEMPERATURE: float = 0.7
    
    # OpenAI配置（可选）
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7
    
    # Claude配置（可选）
    CLAUDE_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-3-sonnet-20240229"
    CLAUDE_MAX_TOKENS: int = 2000
    CLAUDE_TEMPERATURE: float = 0.7
    
    # 邮件服务配置
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False
    
    # 邮件模板配置
    EMAIL_FROM: Optional[str] = None
    EMAIL_FROM_NAME: str = "ChatGalaxy"
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_EXPIRE_HOURS: int = 1
    
    # Redis缓存配置（可选）
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # 文件上传配置
    UPLOAD_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_ALLOWED_EXTENSIONS: List[str] = [
        ".jpg", ".jpeg", ".png", ".gif", ".webp",
        ".pdf", ".doc", ".docx", ".txt", ".md"
    ]
    UPLOAD_PATH: str = "uploads"
    
    # WebSocket配置
    WS_HEARTBEAT_INTERVAL: int = 30  # 心跳间隔（秒）
    WS_HEARTBEAT_TIMEOUT: int = 60   # 心跳超时（秒）
    WS_MAX_CONNECTIONS: int = 1000   # 最大连接数
    WS_MESSAGE_MAX_SIZE: int = 1024 * 1024  # 消息最大大小（1MB）
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # 安全配置
    ALLOWED_HOSTS: List[str] = ["*"]
    TRUSTED_HOSTS: List[str] = ["*"]
    
    # 限流配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # 秒
    
    # 监控配置
    METRICS_ENABLED: bool = False
    HEALTH_CHECK_ENABLED: bool = True
    
    class Config:
        """Pydantic配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """解析CORS源列表"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("UPLOAD_ALLOWED_EXTENSIONS", pre=True)
    def parse_upload_extensions(cls, v):
        """解析上传文件扩展名列表"""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """解析允许的主机列表"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("JWT_SECRET_KEY")
    def validate_jwt_secret(cls, v):
        """验证JWT密钥"""
        if len(v) < 32:
            raise ValueError("JWT密钥长度至少32个字符")
        return v
    
    @validator("QWEN_API_KEY")
    def validate_qwen_api_key(cls, v):
        """验证通义千问API密钥"""
        if not v or len(v) < 10:
            raise ValueError("通义千问API密钥无效")
        return v
    
    @property
    def database_url(self) -> str:
        """获取数据库连接URL"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        # 构建PostgreSQL连接URL
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    @property
    def redis_url(self) -> str:
        """获取Redis连接URL"""
        if self.REDIS_URL:
            return self.REDIS_URL
        
        # 构建Redis连接URL
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def get_ai_config(self, provider: str) -> dict:
        """
        获取AI服务配置
        
        Args:
            provider: AI服务提供商 (qwen, openai, claude)
            
        Returns:
            dict: AI服务配置
        """
        if provider.lower() == "qwen":
            return {
                "api_key": self.QWEN_API_KEY,
                "model": self.QWEN_MODEL,
                "max_tokens": self.QWEN_MAX_TOKENS,
                "temperature": self.QWEN_TEMPERATURE
            }
        elif provider.lower() == "openai":
            return {
                "api_key": self.OPENAI_API_KEY,
                "model": self.OPENAI_MODEL,
                "max_tokens": self.OPENAI_MAX_TOKENS,
                "temperature": self.OPENAI_TEMPERATURE
            }
        elif provider.lower() == "claude":
            return {
                "api_key": self.CLAUDE_API_KEY,
                "model": self.CLAUDE_MODEL,
                "max_tokens": self.CLAUDE_MAX_TOKENS,
                "temperature": self.CLAUDE_TEMPERATURE
            }
        else:
            raise ValueError(f"不支持的AI服务提供商: {provider}")
    
    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.DEBUG or os.getenv("ENVIRONMENT", "").lower() in ["dev", "development"]
    
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return os.getenv("ENVIRONMENT", "").lower() in ["prod", "production"]
    
    def is_testing(self) -> bool:
        """判断是否为测试环境"""
        return os.getenv("ENVIRONMENT", "").lower() in ["test", "testing"]


@lru_cache()
def get_settings() -> Settings:
    """
    获取应用程序配置实例
    
    使用lru_cache装饰器确保单例模式
    
    Returns:
        Settings: 配置实例
    """
    return Settings()


# 导出配置实例
settings = get_settings()


# 环境变量模板（用于文档）
ENV_TEMPLATE = """
# ChatGalaxy 环境变量配置模板
# 复制此文件为 .env 并填入实际值

# 应用程序配置
APP_NAME=ChatGalaxy
APP_VERSION=1.0.0
DEBUG=false

# 服务器配置
HOST=0.0.0.0
PORT=8000

# Supabase配置
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# JWT配置
JWT_SECRET_KEY=your_very_long_and_secure_secret_key_at_least_32_characters
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# AI服务配置
QWEN_API_KEY=your_qwen_api_key
QWEN_MODEL=qwen-turbo

# 可选AI服务
# OPENAI_API_KEY=your_openai_api_key
# CLAUDE_API_KEY=your_claude_api_key

# 邮件服务配置（可选）
# SMTP_USERNAME=your_email@gmail.com
# SMTP_PASSWORD=your_app_password
# EMAIL_FROM=your_email@gmail.com

# Redis配置（可选）
# REDIS_URL=redis://localhost:6379/0

# 日志配置
LOG_LEVEL=INFO

# 环境标识
ENVIRONMENT=development
"""


if __name__ == "__main__":
    # 打印配置模板
    print("ChatGalaxy 环境变量配置模板:")
    print(ENV_TEMPLATE)
    
    # 验证当前配置
    try:
        config = get_settings()
        print(f"\n配置加载成功: {config.APP_NAME} v{config.APP_VERSION}")
        print(f"调试模式: {config.DEBUG}")
        print(f"数据库URL: {config.SUPABASE_URL[:50]}...")
    except Exception as e:
        print(f"\n配置加载失败: {e}")
        print("请检查环境变量配置")