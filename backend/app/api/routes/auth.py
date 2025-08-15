#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 认证路由模块

提供用户认证相关的API端点:
- 用户注册 (POST /register)
- 用户登录 (POST /login)
- 令牌刷新 (POST /refresh)
- 用户登出 (POST /logout)
- 密码重置 (POST /reset-password)
- 邮箱验证 (POST /verify-email)
- 用户信息 (GET /me)
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

from app.core import (
    get_db_client,
    security_manager,
    get_current_user_required,
    verify_refresh_token
)
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.models.user import UserCreate, UserResponse, UserLogin

# 创建路由器
router = APIRouter(prefix="/auth", tags=["认证"])

# 服务实例
auth_service = AuthService()
email_service = EmailService()


class RegisterRequest(BaseModel):
    """
    用户注册请求模型
    """
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    confirm_password: str = Field(..., description="确认密码")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123",
                "username": "测试用户",
                "confirm_password": "password123"
            }
        }


class LoginRequest(BaseModel):
    """
    用户登录请求模型
    """
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")
    remember_me: bool = Field(False, description="记住我")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123",
                "remember_me": False
            }
        }


class TokenResponse(BaseModel):
    """
    令牌响应模型
    """
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")
    user: UserResponse = Field(..., description="用户信息")


class RefreshTokenRequest(BaseModel):
    """
    刷新令牌请求模型
    """
    refresh_token: str = Field(..., description="刷新令牌")


class ResetPasswordRequest(BaseModel):
    """
    重置密码请求模型
    """
    email: EmailStr = Field(..., description="邮箱地址")


class VerifyEmailRequest(BaseModel):
    """
    邮箱验证请求模型
    """
    token: str = Field(..., description="验证令牌")


class ChangePasswordRequest(BaseModel):
    """
    修改密码请求模型
    """
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=128, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="注册新用户账户，返回访问令牌和用户信息"
)
async def register(
    request: RegisterRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db_client)
) -> TokenResponse:
    """
    用户注册
    
    Args:
        request: 注册请求数据
        background_tasks: 后台任务
        db: 数据库客户端
        
    Returns:
        TokenResponse: 令牌和用户信息
        
    Raises:
        HTTPException: 注册失败
    """
    logger.info(f"👤 用户注册请求: {request.email}")
    
    # 验证密码确认
    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码和确认密码不匹配"
        )
    
    try:
        # 检查用户是否已存在
        existing_user = await auth_service.get_user_by_email(db, request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册"
            )
        
        # 创建用户
        user_data = UserCreate(
            email=request.email,
            username=request.username,
            password=request.password
        )
        
        user = await auth_service.create_user(db, user_data)
        
        # 生成令牌
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "is_verified": user.is_verified
        }
        
        tokens = security_manager.create_token_pair(token_data)
        
        # 发送验证邮件(后台任务)
        background_tasks.add_task(
            email_service.send_verification_email,
            user.email,
            user.username,
            user.verification_token
        )
        
        logger.info(f"✅ 用户注册成功: {user.email}")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=3600,  # 1小时
            user=UserResponse.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 用户注册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="用户登录",
    description="用户登录验证，返回访问令牌和用户信息"
)
async def login(
    request: LoginRequest,
    db = Depends(get_db_client)
) -> TokenResponse:
    """
    用户登录
    
    Args:
        request: 登录请求数据
        db: 数据库客户端
        
    Returns:
        TokenResponse: 令牌和用户信息
        
    Raises:
        HTTPException: 登录失败
    """
    logger.info(f"🔐 用户登录请求: {request.email}")
    
    try:
        # 验证用户凭据
        user = await auth_service.authenticate_user(
            db, request.email, request.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户已被禁用"
            )
        
        # 生成令牌
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "is_verified": user.is_verified
        }
        
        tokens = security_manager.create_token_pair(token_data)
        
        # 更新最后登录时间
        await auth_service.update_last_login(db, user.id)
        
        logger.info(f"✅ 用户登录成功: {user.email}")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=3600,  # 1小时
            user=UserResponse.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 用户登录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="刷新令牌",
    description="使用刷新令牌获取新的访问令牌"
)
async def refresh_token(
    payload: Dict[str, Any] = Depends(verify_refresh_token),
    db = Depends(get_db_client)
) -> TokenResponse:
    """
    刷新访问令牌
    
    Args:
        payload: 刷新令牌载荷
        db: 数据库客户端
        
    Returns:
        TokenResponse: 新的令牌和用户信息
        
    Raises:
        HTTPException: 刷新失败
    """
    user_id = payload.get("sub")
    logger.info(f"🔄 令牌刷新请求: 用户={user_id}")
    
    try:
        # 获取用户信息
        user = await auth_service.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用"
            )
        
        # 生成新令牌
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "is_verified": user.is_verified
        }
        
        tokens = security_manager.create_token_pair(token_data)
        
        logger.info(f"✅ 令牌刷新成功: 用户={user.email}")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=3600,  # 1小时
            user=UserResponse.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 令牌刷新失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌刷新失败，请重新登录"
        )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="用户登出",
    description="用户登出，使令牌失效"
)
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    用户登出
    
    Args:
        current_user: 当前用户信息
    """
    user_id = current_user.get("sub")
    logger.info(f"👋 用户登出: 用户={user_id}")
    
    # TODO: 实现令牌黑名单机制
    # 目前只是记录日志，实际应用中需要将令牌加入黑名单
    
    logger.info(f"✅ 用户登出成功: 用户={user_id}")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取用户信息",
    description="获取当前登录用户的详细信息"
)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user_required),
    db = Depends(get_db_client)
) -> UserResponse:
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户信息
        db: 数据库客户端
        
    Returns:
        UserResponse: 用户详细信息
        
    Raises:
        HTTPException: 获取失败
    """
    user_id = current_user.get("sub")
    logger.debug(f"👤 获取用户信息: 用户={user_id}")
    
    try:
        user = await auth_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取用户信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败"
        )


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="重置密码",
    description="发送密码重置邮件"
)
async def reset_password(
    request: ResetPasswordRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db_client)
):
    """
    重置密码
    
    Args:
        request: 重置密码请求
        background_tasks: 后台任务
        db: 数据库客户端
        
    Returns:
        Dict: 操作结果
    """
    logger.info(f"🔑 密码重置请求: {request.email}")
    
    try:
        # 检查用户是否存在
        user = await auth_service.get_user_by_email(db, request.email)
        if user:
            # 生成重置令牌
            reset_token = await auth_service.create_reset_token(db, user.id)
            
            # 发送重置邮件(后台任务)
            background_tasks.add_task(
                email_service.send_password_reset_email,
                user.email,
                user.username,
                reset_token
            )
        
        # 无论用户是否存在都返回成功，防止邮箱枚举攻击
        logger.info(f"✅ 密码重置邮件已发送: {request.email}")
        
        return {"message": "如果该邮箱已注册，您将收到密码重置邮件"}
        
    except Exception as e:
        logger.error(f"❌ 密码重置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码重置失败，请稍后重试"
        )


@router.post(
    "/verify-email",
    status_code=status.HTTP_200_OK,
    summary="验证邮箱",
    description="验证用户邮箱地址"
)
async def verify_email(
    request: VerifyEmailRequest,
    db = Depends(get_db_client)
):
    """
    验证邮箱
    
    Args:
        request: 邮箱验证请求
        db: 数据库客户端
        
    Returns:
        Dict: 验证结果
        
    Raises:
        HTTPException: 验证失败
    """
    logger.info(f"📧 邮箱验证请求: 令牌={request.token[:20]}...")
    
    try:
        # 验证邮箱
        result = await auth_service.verify_email(db, request.token)
        
        if result:
            logger.info("✅ 邮箱验证成功")
            return {"message": "邮箱验证成功"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证令牌无效或已过期"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 邮箱验证失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="邮箱验证失败，请稍后重试"
        )


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="修改密码",
    description="修改用户密码"
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required),
    db = Depends(get_db_client)
):
    """
    修改密码
    
    Args:
        request: 修改密码请求
        current_user: 当前用户信息
        db: 数据库客户端
        
    Returns:
        Dict: 操作结果
        
    Raises:
        HTTPException: 修改失败
    """
    user_id = current_user.get("sub")
    logger.info(f"🔐 修改密码请求: 用户={user_id}")
    
    # 验证新密码确认
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码和确认密码不匹配"
        )
    
    try:
        # 验证旧密码并更新
        result = await auth_service.change_password(
            db, user_id, request.old_password, request.new_password
        )
        
        if result:
            logger.info(f"✅ 密码修改成功: 用户={user_id}")
            return {"message": "密码修改成功"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 密码修改失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码修改失败，请稍后重试"
        )