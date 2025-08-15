#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 主应用程序入口

初始化FastAPI应用程序:
- 配置CORS
- 注册API路由
- 设置中间件
- 配置异常处理
- 启动WebSocket服务
"""

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import traceback


from .core.config import get_settings
from .utils.logger import get_logger, log_request, log_error
from .utils.response import error_response
from .core.database import get_database_manager
from .services.ai_client import get_ai_client, close_ai_client

# 导入API路由
from .api.auth import router as auth_router
from .api.chat import router as chat_router
from .api.routes.roles import router as roles_router
from .api.routes.system import router as system_router
from .websocket.routes import router as websocket_router

# 获取配置和日志
settings = get_settings()
logger = get_logger("chatgalaxy.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用程序生命周期管理
    
    Args:
        app: FastAPI应用实例
    """
    # 启动时初始化
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    
    try:
        # 初始化数据库连接
        db_manager = get_database_manager()
        await db_manager.initialize()
        logger.info("数据库连接初始化成功")
        
        # 初始化AI客户端
        await get_ai_client()
        logger.info("AI客户端初始化成功")
        
        logger.info("应用程序启动完成")
        
    except Exception as e:
        logger.error(f"应用程序启动失败: {e}")
        log_error(e, {"stage": "startup"})
        raise
    
    yield
    
    # 关闭时清理
    logger.info("正在关闭应用程序...")
    
    try:
        # 关闭AI客户端
        await close_ai_client()
        logger.info("AI客户端已关闭")
        
        # 关闭数据库连接
        db_manager = get_database_manager()
        await db_manager.close()
        logger.info("数据库连接已关闭")
        
        logger.info("应用程序关闭完成")
        
    except Exception as e:
        logger.error(f"应用程序关闭时出错: {e}")
        log_error(e, {"stage": "shutdown"})


def create_app() -> FastAPI:
    """
    创建FastAPI应用实例
    
    Returns:
        FastAPI: 配置完成的应用实例
    """
    # 创建FastAPI应用
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # 配置CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_allowed_origins_list(),
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )
    
    # 配置受信任主机中间件
    if settings.TRUSTED_HOSTS != ["*"]:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.TRUSTED_HOSTS
        )
    
    # 添加请求日志中间件
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """
        记录HTTP请求日志
        
        Args:
            request: HTTP请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            Response: HTTP响应对象
        """
        start_time = time.time()
        
        # 获取用户ID（如果已认证）
        user_id = getattr(request.state, "user_id", None)
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # 记录请求日志
            log_request(
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                duration=duration,
                user_id=user_id
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # 记录错误日志
            log_error(e, {
                "method": request.method,
                "path": str(request.url.path),
                "duration": duration,
                "user_id": user_id
            })
            
            # 返回500错误
            return JSONResponse(
                status_code=500,
                content=error_response(
                    message="内部服务器错误",
                    error_code="INTERNAL_SERVER_ERROR"
                )
            )
    
    # 注册API路由
    app.include_router(
        auth_router,
        prefix="/api/auth",
        tags=["认证"]
    )
    
    app.include_router(
        chat_router,
        prefix="/api/chat",
        tags=["聊天"]
    )
    
    app.include_router(
        roles_router,
        prefix="/api/roles",
        tags=["角色"]
    )
    
    app.include_router(
        system_router,
        prefix="/api/system",
        tags=["系统"]
    )
    
    app.include_router(
        websocket_router,
        prefix="/ws",
        tags=["WebSocket"]
    )
    
    # 配置异常处理器
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        HTTP异常处理器
        
        Args:
            request: HTTP请求对象
            exc: HTTP异常对象
            
        Returns:
            JSONResponse: 错误响应
        """
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                message=exc.detail,
                error_code=f"HTTP_{exc.status_code}"
            )
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        请求验证异常处理器
        
        Args:
            request: HTTP请求对象
            exc: 验证异常对象
            
        Returns:
            JSONResponse: 错误响应
        """
        return JSONResponse(
            status_code=422,
            content=error_response(
                message="请求参数验证失败",
                error_code="VALIDATION_ERROR",
                details=exc.errors()
            )
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        通用异常处理器
        
        Args:
            request: HTTP请求对象
            exc: 异常对象
            
        Returns:
            JSONResponse: 错误响应
        """
        # 记录异常详情
        log_error(exc, {
            "method": request.method,
            "path": str(request.url.path),
            "traceback": traceback.format_exc()
        })
        
        return JSONResponse(
            status_code=500,
            content=error_response(
                message="内部服务器错误" if not settings.DEBUG else str(exc),
                error_code="INTERNAL_SERVER_ERROR"
            )
        )
    
    # 根路径健康检查
    @app.get("/", tags=["健康检查"])
    async def root():
        """
        根路径健康检查
        
        Returns:
            dict: 应用信息
        """
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "description": settings.APP_DESCRIPTION,
            "status": "running",
            "debug": settings.DEBUG
        }
    
    # 健康检查端点
    @app.get("/health", tags=["健康检查"])
    async def health_check():
        """
        详细健康检查
        
        Returns:
            dict: 系统健康状态
        """
        try:
            # 检查数据库连接
            db_manager = get_database_manager()
            db_status = "connected" if db_manager.is_connected() else "disconnected"
            
            # 检查AI服务
            ai_client = await get_ai_client()
            ai_status = "available" if ai_client else "unavailable"
            
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "services": {
                    "database": db_status,
                    "ai_service": ai_status
                },
                "version": settings.APP_VERSION
            }
            
        except Exception as e:
            log_error(e, {"endpoint": "/health"})
            return {
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e),
                "version": settings.APP_VERSION
            }
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    # 直接运行时启动开发服务器
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD or settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )