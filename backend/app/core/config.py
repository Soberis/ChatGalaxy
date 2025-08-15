#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 核心配置模块

管理应用的所有配置项，包括:
- 应用基础配置
- 数据库连接配置
- JWT认证配置
- AI服务配置
- WebSocket配置
- 日志配置
"""

from typing import List, Optional
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    应用配置类
    
    使用 Pydantic BaseSettings 自动从环境变量加载配置
    支持 .env 文件和系统环境变量
    """
    
    # 应用基础配置
    APP_NAME: str = "ChatGalaxy"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS配置
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="允许的跨域来源，逗号分隔"
    )
    
    def get_allowed_origins_list(self) -> List[str]:
        """
        获取ALLOWED_ORIGINS的列表格式
        """
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',') if origin.strip()]
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS: List[str] = ["*"]
    
    # Supabase数据库配置
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    
    # JWT认证配置
    SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 阿里通义千问API配置
    QWEN_API_KEY: Optional[str] = None
    QWEN_MODEL: str = "qwen-turbo"
    QWEN_MAX_TOKENS: int = 2000
    QWEN_TEMPERATURE: float = 0.7
    
    # WebSocket配置
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    WEBSOCKET_MAX_CONNECTIONS: int = 1000
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/chatgalaxy.log"
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"
    
    # Redis缓存配置(可选)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "uploads/"
    ALLOWED_FILE_TYPES: List[str] = [
        "jpg", "jpeg", "png", "gif", "pdf", "txt", "doc", "docx"
    ]
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """
        解析CORS允许的源地址
        
        Args:
            v: 原始值，可能是字符串或列表
            
        Returns:
            List[str]: 解析后的源地址列表
        """
        # 如果已经是列表，直接返回
        if isinstance(v, list):
            return v
            
        # 如果是字符串，尝试解析
        if isinstance(v, str):
            # 尝试解析为JSON
            try:
                import json
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass
                
            # 尝试按逗号分隔
            return [origin.strip() for origin in v.split(",")]
            
        # 默认返回空列表
        return []
    
    @field_validator("ALLOWED_METHODS", mode="before")
    @classmethod
    def parse_cors_methods(cls, v):
        """
        解析CORS允许的HTTP方法
        
        Args:
            v: 原始值，可能是字符串或列表
            
        Returns:
            List[str]: 解析后的方法列表
        """
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v
    
    @field_validator("ALLOWED_FILE_TYPES", mode="before")
    @classmethod
    def parse_file_types(cls, v):
        """
        解析允许的文件类型
        
        Args:
            v: 原始值，可能是字符串或列表
            
        Returns:
            List[str]: 解析后的文件类型列表
        """
        if isinstance(v, str):
            return [file_type.strip() for file_type in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        """
        判断是否为生产环境
        
        Returns:
            bool: 是否为生产环境
        """
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """
        判断是否为开发环境
        
        Returns:
            bool: 是否为开发环境
        """
        return self.ENVIRONMENT.lower() == "development"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """
    获取应用配置实例
    
    使用 lru_cache 装饰器确保配置只加载一次
    
    Returns:
        Settings: 配置实例
    """
    return Settings()


# 全局配置实例
settings = get_settings()


# 配置验证函数
def validate_config() -> bool:
    """
    验证关键配置项是否正确设置
    
    Returns:
        bool: 配置是否有效
    """
    errors = []
    
    # 检查必需的配置项
    if not settings.SECRET_KEY or settings.SECRET_KEY == "your-super-secret-jwt-key-change-this-in-production":
        errors.append("SECRET_KEY 必须设置为安全的密钥")
    
    if settings.is_production:
        if not settings.SUPABASE_URL:
            errors.append("生产环境必须配置 SUPABASE_URL")
        
        if not settings.SUPABASE_SERVICE_ROLE_KEY:
            errors.append("生产环境必须配置 SUPABASE_SERVICE_ROLE_KEY")
        
        if not settings.QWEN_API_KEY:
            errors.append("生产环境必须配置 QWEN_API_KEY")
    
    if errors:
        for error in errors:
            print(f"❌ 配置错误: {error}")
        return False
    
    print("✅ 配置验证通过")
    return True


if __name__ == "__main__":
    """
    直接运行时显示当前配置
    """
    print(f"应用名称: {settings.APP_NAME}")
    print(f"版本: {settings.APP_VERSION}")
    print(f"环境: {settings.ENVIRONMENT}")
    print(f"调试模式: {settings.DEBUG}")
    print(f"主机: {settings.HOST}")
    print(f"端口: {settings.PORT}")
    
    validate_config()