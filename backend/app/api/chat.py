#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 聊天API模块

提供聊天相关的API接口:
- 发送消息
- 获取聊天历史
- 会话管理
- AI对话处理
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.security import HTTPBearer
from typing import List, Optional, Dict, Any
import uuid
import time
from datetime import datetime

from ..models.chat_message import (
    ChatMessageCreate, ChatMessageResponse, ChatMessageUpdate,
    MessageType, MessageStatus
)
from ..models.chat_session import (
    ChatSessionCreate, ChatSessionResponse, ChatSessionUpdate
)
from ..models.user import UserResponse
from ..services.chat_service import get_chat_service
from ..services.auth_service import get_current_user
from ..services.ai_client import get_ai_client
from ..utils.response import (
    success_response, error_response, paginated_response
)
from ..utils.logger import get_logger, log_error, log_ai_request
from ..config import get_settings

# 创建路由器
router = APIRouter()
security = HTTPBearer()
settings = get_settings()
logger = get_logger("chatgalaxy.chat")


@router.post("/sessions", response_model=Dict[str, Any])
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: Optional[UserResponse] = Depends(get_current_user)
):
    """
    创建新的聊天会话
    
    Args:
        session_data: 会话创建数据
        current_user: 当前用户（可选，支持访客模式）
        
    Returns:
        Dict[str, Any]: 创建的会话信息
    """
    try:
        chat_service = get_chat_service()
        
        # 为访客用户生成临时用户ID
        user_id = current_user.id if current_user else None
        
        # 创建会话
        session = await chat_service.create_session(
            title=session_data.title,
            ai_role_id=session_data.ai_role_id,
            user_id=user_id,
            metadata=session_data.metadata
        )
        
        logger.info(f"创建聊天会话成功: {session.id}, 用户: {user_id or 'guest'}")
        
        return success_response(
            data=session.dict(),
            message="会话创建成功"
        )
        
    except ValueError as e:
        logger.warning(f"创建会话参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log_error(e, {"action": "create_session", "user_id": current_user.id if current_user else None})
        raise HTTPException(status_code=500, detail="创建会话失败")


@router.get("/sessions", response_model=Dict[str, Any])
async def get_chat_sessions(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    获取用户的聊天会话列表
    
    Args:
        page: 页码
        size: 每页数量
        current_user: 当前用户
        
    Returns:
        Dict[str, Any]: 分页的会话列表
    """
    try:
        chat_service = get_chat_service()
        
        # 获取用户会话列表
        sessions, total = await chat_service.get_user_sessions(
            user_id=current_user.id,
            page=page,
            size=size
        )
        
        return paginated_response(
            data=[session.dict() for session in sessions],
            total=total,
            page=page,
            size=size,
            message="获取会话列表成功"
        )
        
    except Exception as e:
        log_error(e, {"action": "get_sessions", "user_id": current_user.id})
        raise HTTPException(status_code=500, detail="获取会话列表失败")


@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_chat_session(
    session_id: str,
    current_user: Optional[UserResponse] = Depends(get_current_user)
):
    """
    获取指定聊天会话详情
    
    Args:
        session_id: 会话ID
        current_user: 当前用户（可选，支持访客模式）
        
    Returns:
        Dict[str, Any]: 会话详情
    """
    try:
        chat_service = get_chat_service()
        
        # 获取会话详情
        session = await chat_service.get_session(
            session_id=session_id,
            user_id=current_user.id if current_user else None
        )
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return success_response(
            data=session.dict(),
            message="获取会话详情成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"action": "get_session", "session_id": session_id})
        raise HTTPException(status_code=500, detail="获取会话详情失败")


@router.put("/sessions/{session_id}", response_model=Dict[str, Any])
async def update_chat_session(
    session_id: str,
    session_data: ChatSessionUpdate,
    current_user: Optional[UserResponse] = Depends(get_current_user)
):
    """
    更新聊天会话信息
    
    Args:
        session_id: 会话ID
        session_data: 会话更新数据
        current_user: 当前用户（可选，支持访客模式）
        
    Returns:
        Dict[str, Any]: 更新后的会话信息
    """
    try:
        chat_service = get_chat_service()
        
        # 更新会话
        session = await chat_service.update_session(
            session_id=session_id,
            user_id=current_user.id if current_user else None,
            **session_data.dict(exclude_unset=True)
        )
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        logger.info(f"更新会话成功: {session_id}")
        
        return success_response(
            data=session.dict(),
            message="会话更新成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"action": "update_session", "session_id": session_id})
        raise HTTPException(status_code=500, detail="更新会话失败")


@router.delete("/sessions/{session_id}", response_model=Dict[str, Any])
async def delete_chat_session(
    session_id: str,
    current_user: Optional[UserResponse] = Depends(get_current_user)
):
    """
    删除聊天会话
    
    Args:
        session_id: 会话ID
        current_user: 当前用户（可选，支持访客模式）
        
    Returns:
        Dict[str, Any]: 删除结果
    """
    try:
        chat_service = get_chat_service()
        
        # 删除会话
        success = await chat_service.delete_session(
            session_id=session_id,
            user_id=current_user.id if current_user else None
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        logger.info(f"删除会话成功: {session_id}")
        
        return success_response(
            message="会话删除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"action": "delete_session", "session_id": session_id})
        raise HTTPException(status_code=500, detail="删除会话失败")


@router.post("/send", response_model=Dict[str, Any])
async def send_message(
    message_data: ChatMessageCreate,
    background_tasks: BackgroundTasks,
    current_user: Optional[UserResponse] = Depends(get_current_user)
):
    """
    发送聊天消息
    
    Args:
        message_data: 消息数据
        background_tasks: 后台任务
        current_user: 当前用户（可选，支持访客模式）
        
    Returns:
        Dict[str, Any]: 发送结果和AI回复
    """
    try:
        chat_service = get_chat_service()
        ai_client = await get_ai_client()
        
        # 验证会话存在
        session = await chat_service.get_session(
            session_id=message_data.session_id,
            user_id=current_user.id if current_user else None
        )
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 保存用户消息
        user_message = await chat_service.create_message(
            session_id=message_data.session_id,
            content=message_data.content,
            message_type=MessageType.USER,
            ai_role_id=message_data.ai_role_id,
            metadata=message_data.metadata
        )
        
        logger.info(f"用户消息已保存: {user_message.id}")
        
        # 获取聊天历史
        chat_history = await chat_service.get_session_messages(
            session_id=message_data.session_id,
            limit=10  # 最近10条消息作为上下文
        )
        
        # 构建AI请求上下文
        context_messages = []
        for msg in chat_history:
            if msg.message_type == MessageType.USER:
                context_messages.append({"role": "user", "content": msg.content})
            elif msg.message_type == MessageType.ASSISTANT:
                context_messages.append({"role": "assistant", "content": msg.content})
        
        # 添加当前用户消息
        context_messages.append({"role": "user", "content": message_data.content})
        
        # 调用AI服务生成回复
        start_time = time.time()
        ai_response = await ai_client.generate_response(
            messages=context_messages,
            ai_role_id=message_data.ai_role_id
        )
        duration = time.time() - start_time
        
        # 记录AI请求日志
        log_ai_request(
            model=ai_response.model,
            tokens_used=ai_response.tokens_used,
            duration=duration,
            user_id=current_user.id if current_user else None
        )
        
        # 保存AI回复消息
        ai_message = await chat_service.create_message(
            session_id=message_data.session_id,
            content=ai_response.content,
            message_type=MessageType.ASSISTANT,
            ai_role_id=message_data.ai_role_id,
            parent_message_id=user_message.id,
            tokens_used=ai_response.tokens_used,
            metadata={
                "model": ai_response.model,
                "duration": duration,
                "finish_reason": ai_response.finish_reason
            }
        )
        
        logger.info(f"AI回复已保存: {ai_message.id}")
        
        # 后台任务：更新会话标题（如果是第一条消息）
        if len(chat_history) == 0:
            background_tasks.add_task(
                update_session_title,
                session.id,
                message_data.content
            )
        
        return success_response(
            data={
                "user_message": user_message.dict(),
                "ai_message": ai_message.dict(),
                "session_id": message_data.session_id
            },
            message="消息发送成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {
            "action": "send_message",
            "session_id": message_data.session_id,
            "user_id": current_user.id if current_user else None
        })
        raise HTTPException(status_code=500, detail="发送消息失败")


@router.get("/sessions/{session_id}/messages", response_model=Dict[str, Any])
async def get_session_messages(
    session_id: str,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(50, ge=1, le=100, description="每页数量"),
    current_user: Optional[UserResponse] = Depends(get_current_user)
):
    """
    获取会话的聊天消息历史
    
    Args:
        session_id: 会话ID
        page: 页码
        size: 每页数量
        current_user: 当前用户（可选，支持访客模式）
        
    Returns:
        Dict[str, Any]: 分页的消息列表
    """
    try:
        chat_service = get_chat_service()
        
        # 验证会话存在和权限
        session = await chat_service.get_session(
            session_id=session_id,
            user_id=current_user.id if current_user else None
        )
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 获取消息列表
        messages, total = await chat_service.get_session_messages_paginated(
            session_id=session_id,
            page=page,
            size=size
        )
        
        return paginated_response(
            data=[message.dict() for message in messages],
            total=total,
            page=page,
            size=size,
            message="获取消息历史成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {
            "action": "get_messages",
            "session_id": session_id,
            "user_id": current_user.id if current_user else None
        })
        raise HTTPException(status_code=500, detail="获取消息历史失败")


@router.put("/messages/{message_id}", response_model=Dict[str, Any])
async def update_message(
    message_id: str,
    message_data: ChatMessageUpdate,
    current_user: Optional[UserResponse] = Depends(get_current_user)
):
    """
    更新聊天消息
    
    Args:
        message_id: 消息ID
        message_data: 消息更新数据
        current_user: 当前用户（可选，支持访客模式）
        
    Returns:
        Dict[str, Any]: 更新后的消息信息
    """
    try:
        chat_service = get_chat_service()
        
        # 更新消息
        message = await chat_service.update_message(
            message_id=message_id,
            user_id=current_user.id if current_user else None,
            **message_data.dict(exclude_unset=True)
        )
        
        if not message:
            raise HTTPException(status_code=404, detail="消息不存在")
        
        logger.info(f"更新消息成功: {message_id}")
        
        return success_response(
            data=message.dict(),
            message="消息更新成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {
            "action": "update_message",
            "message_id": message_id,
            "user_id": current_user.id if current_user else None
        })
        raise HTTPException(status_code=500, detail="更新消息失败")


@router.delete("/messages/{message_id}", response_model=Dict[str, Any])
async def delete_message(
    message_id: str,
    current_user: Optional[UserResponse] = Depends(get_current_user)
):
    """
    删除聊天消息
    
    Args:
        message_id: 消息ID
        current_user: 当前用户（可选，支持访客模式）
        
    Returns:
        Dict[str, Any]: 删除结果
    """
    try:
        chat_service = get_chat_service()
        
        # 删除消息
        success = await chat_service.delete_message(
            message_id=message_id,
            user_id=current_user.id if current_user else None
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="消息不存在")
        
        logger.info(f"删除消息成功: {message_id}")
        
        return success_response(
            message="消息删除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {
            "action": "delete_message",
            "message_id": message_id,
            "user_id": current_user.id if current_user else None
        })
        raise HTTPException(status_code=500, detail="删除消息失败")


async def update_session_title(session_id: str, first_message: str):
    """
    后台任务：根据第一条消息更新会话标题
    
    Args:
        session_id: 会话ID
        first_message: 第一条消息内容
    """
    try:
        chat_service = get_chat_service()
        
        # 生成会话标题（取前30个字符）
        title = first_message[:30] + "..." if len(first_message) > 30 else first_message
        
        # 更新会话标题
        await chat_service.update_session(
            session_id=session_id,
            user_id=None,  # 后台任务不需要用户验证
            title=title
        )
        
        logger.info(f"会话标题更新成功: {session_id} -> {title}")
        
    except Exception as e:
        log_error(e, {
            "action": "update_session_title",
            "session_id": session_id
        })