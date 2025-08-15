#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy AI角色路由模块

提供AI角色管理相关的API端点:
- 获取角色列表 (GET /)
- 获取角色详情 (GET /{role_id})
- 创建角色 (POST /) [管理员]
- 更新角色 (PUT /{role_id}) [管理员]
- 删除角色 (DELETE /{role_id}) [管理员]
- 角色配置管理 (GET/PUT /config)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from loguru import logger

from app.core import get_db_client, get_admin_user
from app.services.role_service import RoleService
from app.models.role import (
    AIRoleCreate,
    AIRoleUpdate,
    AIRoleResponse
)

# 创建路由器
router = APIRouter(prefix="/roles", tags=["AI角色"])

# 服务实例
role_service = RoleService()


class RoleListResponse(BaseModel):
    """
    角色列表响应模型
    """
    roles: List[AIRoleResponse] = Field(..., description="角色列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")


class CreateRoleRequest(BaseModel):
    """
    创建角色请求模型
    """
    name: str = Field(..., min_length=1, max_length=100, description="角色名称")
    description: str = Field(..., min_length=1, max_length=500, description="角色描述")
    avatar: Optional[str] = Field(None, max_length=500, description="角色头像URL")
    system_prompt: str = Field(..., min_length=1, max_length=2000, description="系统提示词")
    personality: Optional[str] = Field(None, max_length=500, description="角色性格特点")
    expertise: Optional[List[str]] = Field(None, description="专业领域")
    greeting: Optional[str] = Field(None, max_length=200, description="问候语")
    is_active: bool = Field(True, description="是否启用")
    is_default: bool = Field(False, description="是否为默认角色")
    config: Optional[Dict[str, Any]] = Field(None, description="角色配置")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "技术专家",
                "description": "专业的技术顾问，擅长解答编程和技术问题",
                "avatar": "https://example.com/avatar/tech.png",
                "system_prompt": "你是一个专业的技术专家，具有丰富的编程经验。请用专业但易懂的方式回答技术问题，提供实用的解决方案。",
                "personality": "专业、耐心、逻辑清晰",
                "expertise": ["Python", "JavaScript", "数据库", "系统架构"],
                "greeting": "你好！我是技术专家，有什么技术问题需要帮助吗？",
                "is_active": True,
                "is_default": False,
                "config": {
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "top_p": 0.9
                }
            }
        }


class UpdateRoleRequest(BaseModel):
    """
    更新角色请求模型
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="角色名称")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="角色描述")
    avatar: Optional[str] = Field(None, max_length=500, description="角色头像URL")
    system_prompt: Optional[str] = Field(None, min_length=1, max_length=2000, description="系统提示词")
    personality: Optional[str] = Field(None, max_length=500, description="角色性格特点")
    expertise: Optional[List[str]] = Field(None, description="专业领域")
    greeting: Optional[str] = Field(None, max_length=200, description="问候语")
    is_active: Optional[bool] = Field(None, description="是否启用")
    is_default: Optional[bool] = Field(None, description="是否为默认角色")
    config: Optional[Dict[str, Any]] = Field(None, description="角色配置")


class RoleConfigResponse(BaseModel):
    """
    角色配置响应模型
    """
    default_role_id: Optional[str] = Field(None, description="默认角色ID")
    max_roles_per_user: int = Field(10, description="每用户最大角色数")
    allow_custom_roles: bool = Field(False, description="是否允许自定义角色")
    role_categories: List[str] = Field(default_factory=list, description="角色分类")
    featured_roles: List[str] = Field(default_factory=list, description="推荐角色ID列表")
    config: Dict[str, Any] = Field(default_factory=dict, description="其他配置")


@router.get(
    "/",
    response_model=RoleListResponse,
    summary="获取AI角色列表",
    description="获取可用的AI角色列表，支持分页和筛选"
)
async def get_roles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    category: Optional[str] = Query(None, description="角色分类"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db = Depends(get_db_client)
) -> RoleListResponse:
    """
    获取AI角色列表
    
    Args:
        page: 页码
        page_size: 每页大小
        is_active: 是否启用筛选
        category: 角色分类筛选
        search: 搜索关键词
        db: 数据库客户端
        
    Returns:
        RoleListResponse: 角色列表
    """
    logger.debug(f"🎭 获取AI角色列表: 页码={page}, 筛选={is_active}")
    
    try:
        # 构建筛选条件
        filters = {}
        if is_active is not None:
            filters['is_active'] = is_active
        if category:
            filters['category'] = category
        if search:
            filters['search'] = search
        
        # 获取角色列表
        roles, total = await role_service.get_roles(
            db, page, page_size, filters
        )
        
        return RoleListResponse(
            roles=[AIRoleResponse.from_orm(role) for role in roles],
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"❌ 获取AI角色列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色列表失败"
        )


@router.get(
    "/{role_id}",
    response_model=AIRoleResponse,
    summary="获取AI角色详情",
    description="获取指定AI角色的详细信息"
)
async def get_role(
    role_id: str,
    db = Depends(get_db_client)
) -> AIRoleResponse:
    """
    获取AI角色详情
    
    Args:
        role_id: 角色ID
        db: 数据库客户端
        
    Returns:
        AIRoleResponse: 角色详情
        
    Raises:
        HTTPException: 角色不存在
    """
    logger.debug(f"🔍 获取AI角色详情: ID={role_id}")
    
    try:
        # 获取角色
        role = await role_service.get_role(db, role_id)
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        return AIRoleResponse.from_orm(role)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取AI角色详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色详情失败"
        )


@router.post(
    "/",
    response_model=AIRoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建AI角色",
    description="创建新的AI角色（需要管理员权限）"
)
async def create_role(
    request: CreateRoleRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    db = Depends(get_db_client)
) -> AIRoleResponse:
    """
    创建AI角色
    
    Args:
        request: 创建角色请求
        admin_user: 管理员用户信息
        db: 数据库客户端
        
    Returns:
        AIRoleResponse: 创建的角色信息
        
    Raises:
        HTTPException: 创建失败
    """
    admin_id = admin_user.get("sub")
    logger.info(f"🎭 创建AI角色: 管理员={admin_id}, 角色名={request.name}")
    
    try:
        # 检查角色名是否已存在
        existing_role = await role_service.get_role_by_name(db, request.name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色名称已存在"
            )
        
        # 创建角色数据
        role_data = AIRoleCreate(
            name=request.name,
            description=request.description,
            avatar=request.avatar,
            system_prompt=request.system_prompt,
            personality=request.personality,
            expertise=request.expertise or [],
            greeting=request.greeting,
            is_active=request.is_active,
            is_default=request.is_default,
            config=request.config or {},
            created_by=admin_id
        )
        
        # 创建角色
        role = await role_service.create_role(db, role_data)
        
        logger.info(f"✅ AI角色创建成功: ID={role.id}, 名称={role.name}")
        return AIRoleResponse.from_orm(role)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 创建AI角色失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建角色失败，请稍后重试"
        )


@router.put(
    "/{role_id}",
    response_model=AIRoleResponse,
    summary="更新AI角色",
    description="更新指定的AI角色信息（需要管理员权限）"
)
async def update_role(
    role_id: str,
    request: UpdateRoleRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    db = Depends(get_db_client)
) -> AIRoleResponse:
    """
    更新AI角色
    
    Args:
        role_id: 角色ID
        request: 更新角色请求
        admin_user: 管理员用户信息
        db: 数据库客户端
        
    Returns:
        AIRoleResponse: 更新后的角色信息
        
    Raises:
        HTTPException: 更新失败
    """
    admin_id = admin_user.get("sub")
    logger.info(f"✏️ 更新AI角色: ID={role_id}, 管理员={admin_id}")
    
    try:
        # 检查角色是否存在
        existing_role = await role_service.get_role(db, role_id)
        if not existing_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 如果更新名称，检查是否重复
        if request.name and request.name != existing_role.name:
            name_exists = await role_service.get_role_by_name(db, request.name)
            if name_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="角色名称已存在"
                )
        
        # 创建更新数据
        update_data = AIRoleUpdate(
            **{k: v for k, v in request.dict().items() if v is not None}
        )
        update_data.updated_by = admin_id
        
        # 更新角色
        role = await role_service.update_role(db, role_id, update_data)
        
        logger.info(f"✅ AI角色更新成功: ID={role_id}")
        return AIRoleResponse.from_orm(role)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 更新AI角色失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新角色失败，请稍后重试"
        )


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除AI角色",
    description="删除指定的AI角色（需要管理员权限）"
)
async def delete_role(
    role_id: str,
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    db = Depends(get_db_client)
):
    """
    删除AI角色
    
    Args:
        role_id: 角色ID
        admin_user: 管理员用户信息
        db: 数据库客户端
        
    Raises:
        HTTPException: 删除失败
    """
    admin_id = admin_user.get("sub")
    logger.info(f"🗑️ 删除AI角色: ID={role_id}, 管理员={admin_id}")
    
    try:
        # 检查角色是否存在
        existing_role = await role_service.get_role(db, role_id)
        if not existing_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 检查是否为默认角色
        if existing_role.is_default:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除默认角色"
            )
        
        # 检查是否有关联的会话
        session_count = await role_service.get_role_session_count(db, role_id)
        if session_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"角色正在被 {session_count} 个会话使用，无法删除"
            )
        
        # 删除角色
        result = await role_service.delete_role(db, role_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除角色失败"
            )
        
        logger.info(f"✅ AI角色删除成功: ID={role_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除AI角色失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除角色失败"
        )


@router.get(
    "/config",
    response_model=RoleConfigResponse,
    summary="获取角色配置",
    description="获取系统角色配置信息"
)
async def get_role_config(
    db = Depends(get_db_client)
) -> RoleConfigResponse:
    """
    获取角色配置
    
    Args:
        db: 数据库客户端
        
    Returns:
        RoleConfigResponse: 角色配置信息
    """
    logger.debug("⚙️ 获取角色配置")
    
    try:
        # 获取配置
        config = await role_service.get_role_config(db)
        
        return RoleConfigResponse(
            default_role_id=config.get("default_role_id"),
            max_roles_per_user=config.get("max_roles_per_user", 10),
            allow_custom_roles=config.get("allow_custom_roles", False),
            role_categories=config.get("role_categories", []),
            featured_roles=config.get("featured_roles", []),
            config=config.get("config", {})
        )
        
    except Exception as e:
        logger.error(f"❌ 获取角色配置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色配置失败"
        )


@router.put(
    "/config",
    response_model=RoleConfigResponse,
    summary="更新角色配置",
    description="更新系统角色配置（需要管理员权限）"
)
async def update_role_config(
    config: RoleConfigResponse,
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    db = Depends(get_db_client)
) -> RoleConfigResponse:
    """
    更新角色配置
    
    Args:
        config: 角色配置
        admin_user: 管理员用户信息
        db: 数据库客户端
        
    Returns:
        RoleConfigResponse: 更新后的配置
        
    Raises:
        HTTPException: 更新失败
    """
    admin_id = admin_user.get("sub")
    logger.info(f"⚙️ 更新角色配置: 管理员={admin_id}")
    
    try:
        # 更新配置
        updated_config = await role_service.update_role_config(
            db, config.dict(), admin_id
        )
        
        logger.info("✅ 角色配置更新成功")
        return RoleConfigResponse(**updated_config)
        
    except Exception as e:
        logger.error(f"❌ 更新角色配置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新角色配置失败"
        )


@router.get(
    "/featured",
    response_model=List[AIRoleResponse],
    summary="获取推荐角色",
    description="获取系统推荐的AI角色列表"
)
async def get_featured_roles(
    limit: int = Query(6, ge=1, le=20, description="返回数量限制"),
    db = Depends(get_db_client)
) -> List[AIRoleResponse]:
    """
    获取推荐角色
    
    Args:
        limit: 返回数量限制
        db: 数据库客户端
        
    Returns:
        List[AIRoleResponse]: 推荐角色列表
    """
    logger.debug(f"⭐ 获取推荐角色: 限制={limit}")
    
    try:
        # 获取推荐角色
        roles = await role_service.get_featured_roles(db, limit)
        
        return [AIRoleResponse.from_orm(role) for role in roles]
        
    except Exception as e:
        logger.error(f"❌ 获取推荐角色失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取推荐角色失败"
        )


@router.get(
    "/categories",
    response_model=List[str],
    summary="获取角色分类",
    description="获取所有可用的角色分类"
)
async def get_role_categories(
    db = Depends(get_db_client)
) -> List[str]:
    """
    获取角色分类
    
    Args:
        db: 数据库客户端
        
    Returns:
        List[str]: 角色分类列表
    """
    logger.debug("📂 获取角色分类")
    
    try:
        # 获取分类
        categories = await role_service.get_role_categories(db)
        
        return categories
        
    except Exception as e:
        logger.error(f"❌ 获取角色分类失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色分类失败"
        )