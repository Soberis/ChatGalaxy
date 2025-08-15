#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 后端主应用入口
基于 FastAPI 0.104 + Python 3.11+

主要功能:
- FastAPI 应用初始化和配置
- CORS 跨域配置
- API 路由注册
- WebSocket 支持
- 全局异常处理
- 应用生命周期管理
"""

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from pathlib import Path

# 导入配置和核心模块
from app.core.config import settings
from app.core.database import init_database
from app.core.logging import setup_logging

# 导入API路由
from app.api.routes import auth, chat, roles, system
from app.websocket.connection import websocket_router

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    启动时:
    - 初始化数据库连接
    - 创建必要的目录
    - 加载AI模型配置
    
    关闭时:
    - 清理资源
    - 关闭数据库连接
    """
    logger.info("🚀 ChatGalaxy 后端服务启动中...")
    
    try:
        # 初始化数据库
        await init_database()
        logger.info("✅ 数据库连接初始化完成")
        
        # 创建必要的目录
        Path("logs").mkdir(exist_ok=True)
        Path("uploads").mkdir(exist_ok=True)
        logger.info("✅ 目录结构创建完成")
        
        logger.info("🎉 ChatGalaxy 后端服务启动成功!")
        
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        raise
    
    yield
    
    # 应用关闭时的清理工作
    logger.info("🔄 ChatGalaxy 后端服务关闭中...")
    logger.info("👋 ChatGalaxy 后端服务已关闭")


def create_application() -> FastAPI:
    """
    创建并配置 FastAPI 应用实例
    
    Returns:
        FastAPI: 配置完成的应用实例
    """
    # 创建FastAPI应用
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="ChatGalaxy - 多角色AI智能聊天平台后端API",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # 配置CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )
    
    # 注册API路由
    app.include_router(
        auth.router,
        prefix="/api/auth",
        tags=["认证管理"]
    )
    
    app.include_router(
        chat.router,
        prefix="/api/chat",
        tags=["聊天对话"]
    )
    
    app.include_router(
        roles.router,
        prefix="/api/roles",
        tags=["角色管理"]
    )
    
    app.include_router(
        system.router,
        prefix="/api/system",
        tags=["系统管理"]
    )
    
    # 注册WebSocket路由
    app.include_router(
        websocket_router,
        prefix="/ws",
        tags=["WebSocket"]
    )
    
    # 静态文件服务
    if Path("uploads").exists():
        app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    
    return app


# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTP异常处理器
    
    Args:
        request: 请求对象
        exc: HTTP异常
        
    Returns:
        JSONResponse: 标准化的错误响应
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code,
            "timestamp": str(datetime.utcnow())
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    通用异常处理器
    
    Args:
        request: 请求对象
        exc: 异常对象
        
    Returns:
        JSONResponse: 标准化的错误响应
    """
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "error_code": 500,
            "timestamp": str(datetime.utcnow())
        }
    )


# 创建应用实例
app = create_application()


# 健康检查端点
@app.get("/health", tags=["系统"])
async def health_check():
    """
    健康检查端点
    
    Returns:
        dict: 服务状态信息
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": str(datetime.utcnow())
    }


# 根路径
@app.get("/", tags=["系统"])
async def root():
    """
    根路径欢迎信息
    
    Returns:
        dict: 欢迎信息
    """
    return {
        "message": f"欢迎使用 {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "文档已禁用",
        "websocket": "/ws"
    }


if __name__ == "__main__":
    """
    直接运行时的入口点
    """
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )