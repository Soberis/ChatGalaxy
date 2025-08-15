#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 系统管理路由模块

提供系统管理相关的API端点:
- 系统健康检查 (GET /health)
- 系统信息 (GET /info)
- 系统统计 (GET /stats)
- 系统配置 (GET/PUT /config) [管理员]
- 用户管理 (GET/PUT/DELETE /users) [管理员]
- 系统日志 (GET /logs) [管理员]
- 数据备份 (POST /backup) [管理员]
- 系统维护 (POST /maintenance) [管理员]
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger
import psutil
import platform
import sys

from app.core import get_db_client, get_admin_user, settings
from app.services.system_service import SystemService
from app.services.user_service import UserService


# 创建路由器
router = APIRouter(prefix="/system", tags=["系统管理"])

# 服务实例
system_service = SystemService()
user_service = UserService()


class HealthResponse(BaseModel):
    """
    健康检查响应模型
    """
    status: str = Field(..., description="系统状态")
    timestamp: datetime = Field(..., description="检查时间")
    version: str = Field(..., description="系统版本")
    uptime: float = Field(..., description="运行时间(秒)")
    database: str = Field(..., description="数据库状态")
    ai_service: str = Field(..., description="AI服务状态")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-01-27T10:00:00Z",
                "version": "1.0.0",
                "uptime": 3600.0,
                "database": "connected",
                "ai_service": "available"
            }
        }


class SystemInfoResponse(BaseModel):
    """
    系统信息响应模型
    """
    system: Dict[str, Any] = Field(..., description="系统信息")
    hardware: Dict[str, Any] = Field(..., description="硬件信息")
    application: Dict[str, Any] = Field(..., description="应用信息")
    dependencies: Dict[str, str] = Field(..., description="依赖版本")


class SystemStatsResponse(BaseModel):
    """
    系统统计响应模型
    """
    users: Dict[str, int] = Field(..., description="用户统计")
    sessions: Dict[str, int] = Field(..., description="会话统计")
    messages: Dict[str, int] = Field(..., description="消息统计")
    ai_usage: Dict[str, Any] = Field(..., description="AI使用统计")
    performance: Dict[str, float] = Field(..., description="性能指标")
    period: str = Field(..., description="统计周期")


class SystemConfigResponse(BaseModel):
    """
    系统配置响应模型
    """
    app_config: Dict[str, Any] = Field(..., description="应用配置")
    ai_config: Dict[str, Any] = Field(..., description="AI配置")
    security_config: Dict[str, Any] = Field(..., description="安全配置")
    feature_flags: Dict[str, bool] = Field(..., description="功能开关")
    limits: Dict[str, int] = Field(..., description="限制配置")


class UpdateConfigRequest(BaseModel):
    """
    更新配置请求模型
    """
    config_type: str = Field(..., description="配置类型")
    config_data: Dict[str, Any] = Field(..., description="配置数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "config_type": "ai_config",
                "config_data": {
                    "default_model": "qwen-turbo",
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            }
        }


class UserListResponse(BaseModel):
    """
    用户列表响应模型
    """
    users: List[Dict[str, Any]] = Field(..., description="用户列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")


class UpdateUserRequest(BaseModel):
    """
    更新用户请求模型
    """
    is_active: Optional[bool] = Field(None, description="是否启用")
    role: Optional[str] = Field(None, description="用户角色")
    permissions: Optional[List[str]] = Field(None, description="用户权限")
    metadata: Optional[Dict[str, Any]] = Field(None, description="用户元数据")


class LogListResponse(BaseModel):
    """
    日志列表响应模型
    """
    logs: List[Dict[str, Any]] = Field(..., description="日志列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")


class BackupResponse(BaseModel):
    """
    备份响应模型
    """
    backup_id: str = Field(..., description="备份ID")
    status: str = Field(..., description="备份状态")
    created_at: datetime = Field(..., description="创建时间")
    file_path: Optional[str] = Field(None, description="备份文件路径")
    size: Optional[int] = Field(None, description="文件大小")


class MaintenanceRequest(BaseModel):
    """
    维护请求模型
    """
    action: str = Field(..., description="维护操作")
    parameters: Optional[Dict[str, Any]] = Field(None, description="操作参数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "clear_cache",
                "parameters": {"cache_type": "all"}
            }
        }


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="系统健康检查",
    description="检查系统各组件的健康状态"
)
async def health_check(
    db = Depends(get_db_client)
) -> HealthResponse:
    """
    系统健康检查
    
    Args:
        db: 数据库客户端
        
    Returns:
        HealthResponse: 健康状态信息
    """
    logger.debug("🏥 执行系统健康检查")
    
    try:
        # 检查数据库连接
        db_status = "connected" if await system_service.check_database_health(db) else "disconnected"
        
        # 检查AI服务
        ai_status = "available" if await system_service.check_ai_service_health() else "unavailable"
        
        # 计算运行时间
        uptime = await system_service.get_uptime()
        
        # 确定整体状态
        overall_status = "healthy" if db_status == "connected" and ai_status == "available" else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version="1.0.0",
            uptime=uptime,
            database=db_status,
            ai_service=ai_status
        )
        
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            uptime=0.0,
            database="error",
            ai_service="error"
        )


@router.get(
    "/info",
    response_model=SystemInfoResponse,
    summary="获取系统信息",
    description="获取系统的详细信息"
)
async def get_system_info() -> SystemInfoResponse:
    """
    获取系统信息
    
    Returns:
        SystemInfoResponse: 系统信息
    """
    logger.debug("ℹ️ 获取系统信息")
    
    try:
        # 系统信息
        system_info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "python_version": sys.version,
            "python_executable": sys.executable
        }
        
        # 硬件信息
        hardware_info = {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": dict(psutil.disk_usage('/')._asdict()) if platform.system() != "Windows" else dict(psutil.disk_usage('C:')._asdict())
        }
        
        # 应用信息
        app_info = {
            "name": "ChatGalaxy Backend",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "debug_mode": settings.DEBUG,
            "start_time": datetime.utcnow().isoformat(),
            "timezone": str(datetime.now().astimezone().tzinfo)
        }
        
        # 依赖版本
        dependencies = {
            "fastapi": "0.104.1",
            "pydantic": "2.5.0",
            "uvicorn": "0.24.0",
            "supabase": "2.3.0",
            "loguru": "0.7.2"
        }
        
        return SystemInfoResponse(
            system=system_info,
            hardware=hardware_info,
            application=app_info,
            dependencies=dependencies
        )
        
    except Exception as e:
        logger.error(f"❌ 获取系统信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统信息失败"
        )


@router.get(
    "/stats",
    response_model=SystemStatsResponse,
    summary="获取系统统计",
    description="获取系统使用统计信息"
)
async def get_system_stats(
    period: str = Query("24h", description="统计周期: 1h, 24h, 7d, 30d"),
    db = Depends(get_db_client)
) -> SystemStatsResponse:
    """
    获取系统统计
    
    Args:
        period: 统计周期
        db: 数据库客户端
        
    Returns:
        SystemStatsResponse: 统计信息
    """
    logger.debug(f"📊 获取系统统计: 周期={period}")
    
    try:
        # 解析时间周期
        time_delta = {
            "1h": timedelta(hours=1),
            "24h": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }.get(period, timedelta(days=1))
        
        start_time = datetime.utcnow() - time_delta
        
        # 获取统计数据
        stats = await system_service.get_system_stats(db, start_time)
        
        return SystemStatsResponse(
            users=stats.get("users", {}),
            sessions=stats.get("sessions", {}),
            messages=stats.get("messages", {}),
            ai_usage=stats.get("ai_usage", {}),
            performance=stats.get("performance", {}),
            period=period
        )
        
    except Exception as e:
        logger.error(f"❌ 获取系统统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统统计失败"
        )


@router.get(
    "/config",
    response_model=SystemConfigResponse,
    summary="获取系统配置",
    description="获取系统配置信息（需要管理员权限）"
)
async def get_system_config(
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    db = Depends(get_db_client)
) -> SystemConfigResponse:
    """
    获取系统配置
    
    Args:
        admin_user: 管理员用户信息
        db: 数据库客户端
        
    Returns:
        SystemConfigResponse: 系统配置
    """
    logger.debug("⚙️ 获取系统配置")
    
    try:
        # 获取配置
        config = await system_service.get_system_config(db)
        
        return SystemConfigResponse(
            app_config=config.get("app_config", {}),
            ai_config=config.get("ai_config", {}),
            security_config=config.get("security_config", {}),
            feature_flags=config.get("feature_flags", {}),
            limits=config.get("limits", {})
        )
        
    except Exception as e:
        logger.error(f"❌ 获取系统配置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统配置失败"
        )


@router.put(
    "/config",
    response_model=SystemConfigResponse,
    summary="更新系统配置",
    description="更新系统配置（需要管理员权限）"
)
async def update_system_config(
    request: UpdateConfigRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    db = Depends(get_db_client)
) -> SystemConfigResponse:
    """
    更新系统配置
    
    Args:
        request: 更新配置请求
        admin_user: 管理员用户信息
        db: 数据库客户端
        
    Returns:
        SystemConfigResponse: 更新后的配置
    """
    admin_id = admin_user.get("sub")
    logger.info(f"⚙️ 更新系统配置: 类型={request.config_type}, 管理员={admin_id}")
    
    try:
        # 更新配置
        updated_config = await system_service.update_system_config(
            db, request.config_type, request.config_data, admin_id
        )
        
        logger.info(f"✅ 系统配置更新成功: 类型={request.config_type}")
        
        return SystemConfigResponse(
            app_config=updated_config.get("app_config", {}),
            ai_config=updated_config.get("ai_config", {}),
            security_config=updated_config.get("security_config", {}),
            feature_flags=updated_config.get("feature_flags", {}),
            limits=updated_config.get("limits", {})
        )
        
    except Exception as e:
        logger.error(f"❌ 更新系统配置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新系统配置失败"
        )


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="获取用户列表",
    description="获取系统用户列表（需要管理员权限）"
)
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    role: Optional[str] = Query(None, description="角色筛选"),
    is_active: Optional[bool] = Query(None, description="状态筛选"),
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    db = Depends(get_db_client)
) -> UserListResponse:
    """
    获取用户列表
    
    Args:
        page: 页码
        page_size: 每页大小
        search: 搜索关键词
        role: 角色筛选
        is_active: 状态筛选
        admin_user: 管理员用户信息
        db: 数据库客户端
        
    Returns:
        UserListResponse: 用户列表
    """
    logger.debug(f"👥 获取用户列表: 页码={page}, 搜索={search}")
    
    try:
        # 构建筛选条件
        filters = {}
        if search:
            filters['search'] = search
        if role:
            filters['role'] = role
        if is_active is not None:
            filters['is_active'] = is_active
        
        # 获取用户列表
        users, total = await user_service.get_users(
            db, page, page_size, filters
        )
        
        return UserListResponse(
            users=users,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"❌ 获取用户列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表失败"
        )


@router.put(
    "/users/{user_id}",
    summary="更新用户信息",
    description="更新指定用户的信息（需要管理员权限）"
)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    db = Depends(get_db_client)
):
    """
    更新用户信息
    
    Args:
        user_id: 用户ID
        request: 更新请求
        admin_user: 管理员用户信息
        db: 数据库客户端
    """
    admin_id = admin_user.get("sub")
    logger.info(f"✏️ 更新用户信息: ID={user_id}, 管理员={admin_id}")
    
    try:
        # 更新用户
        result = await user_service.update_user(
            db, user_id, request.dict(exclude_unset=True), admin_id
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        logger.info(f"✅ 用户信息更新成功: ID={user_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 更新用户信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户信息失败"
        )


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除用户",
    description="删除指定用户（需要管理员权限）"
)
async def delete_user(
    user_id: str,
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    db = Depends(get_db_client)
):
    """
    删除用户
    
    Args:
        user_id: 用户ID
        admin_user: 管理员用户信息
        db: 数据库客户端
    """
    admin_id = admin_user.get("sub")
    logger.info(f"🗑️ 删除用户: ID={user_id}, 管理员={admin_id}")
    
    try:
        # 删除用户
        result = await user_service.delete_user(db, user_id, admin_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        logger.info(f"✅ 用户删除成功: ID={user_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除用户失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户失败"
        )


@router.get(
    "/logs",
    response_model=LogListResponse,
    summary="获取系统日志",
    description="获取系统日志记录（需要管理员权限）"
)
async def get_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页大小"),
    level: Optional[str] = Query(None, description="日志级别筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    db = Depends(get_db_client)
) -> LogListResponse:
    """
    获取系统日志
    
    Args:
        page: 页码
        page_size: 每页大小
        level: 日志级别筛选
        start_time: 开始时间
        end_time: 结束时间
        admin_user: 管理员用户信息
        db: 数据库客户端
        
    Returns:
        LogListResponse: 日志列表
    """
    logger.debug(f"📋 获取系统日志: 页码={page}, 级别={level}")
    
    try:
        # 构建筛选条件
        filters = {}
        if level:
            filters['level'] = level
        if start_time:
            filters['start_time'] = start_time
        if end_time:
            filters['end_time'] = end_time
        
        # 获取日志
        logs, total = await system_service.get_system_logs(
            db, page, page_size, filters
        )
        
        return LogListResponse(
            logs=logs,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"❌ 获取系统日志失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统日志失败"
        )


@router.post(
    "/backup",
    response_model=BackupResponse,
    summary="创建数据备份",
    description="创建系统数据备份（需要管理员权限）"
)
async def create_backup(
    background_tasks: BackgroundTasks,
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    db = Depends(get_db_client)
) -> BackupResponse:
    """
    创建数据备份
    
    Args:
        background_tasks: 后台任务
        admin_user: 管理员用户信息
        db: 数据库客户端
        
    Returns:
        BackupResponse: 备份信息
    """
    admin_id = admin_user.get("sub")
    logger.info(f"💾 创建数据备份: 管理员={admin_id}")
    
    try:
        # 创建备份任务
        backup_id = await system_service.create_backup_task(db, admin_id)
        
        # 添加后台任务
        background_tasks.add_task(
            system_service.execute_backup,
            db, backup_id
        )
        
        logger.info(f"✅ 备份任务创建成功: ID={backup_id}")
        
        return BackupResponse(
            backup_id=backup_id,
            status="pending",
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"❌ 创建数据备份失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建数据备份失败"
        )


@router.post(
    "/maintenance",
    summary="执行系统维护",
    description="执行系统维护操作（需要管理员权限）"
)
async def system_maintenance(
    request: MaintenanceRequest,
    background_tasks: BackgroundTasks,
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    db = Depends(get_db_client)
):
    """
    执行系统维护
    
    Args:
        request: 维护请求
        background_tasks: 后台任务
        admin_user: 管理员用户信息
        db: 数据库客户端
    """
    admin_id = admin_user.get("sub")
    logger.info(f"🔧 执行系统维护: 操作={request.action}, 管理员={admin_id}")
    
    try:
        # 验证维护操作
        valid_actions = [
            "clear_cache", "cleanup_logs", "optimize_database",
            "restart_services", "update_indexes"
        ]
        
        if request.action not in valid_actions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的维护操作: {request.action}"
            )
        
        # 添加后台维护任务
        background_tasks.add_task(
            system_service.execute_maintenance,
            db, request.action, request.parameters or {}, admin_id
        )
        
        logger.info(f"✅ 维护任务已启动: 操作={request.action}")
        
        return {"message": f"维护任务 '{request.action}' 已启动"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 执行系统维护失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="执行系统维护失败"
        )