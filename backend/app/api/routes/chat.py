#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 聊天路由模块

提供AI聊天相关的API端点:
- 创建聊天会话 (POST /sessions)
- 获取聊天会话列表 (GET /sessions)
- 获取聊天会话详情 (GET /sessions/{session_id})
- 删除聊天会话 (DELETE /sessions/{session_id})
- 发送消息 (POST /sessions/{session_id}/messages)
- 获取消息历史 (GET /sessions/{session_id}/messages)
- 流式聊天 (WebSocket /ws/{session_id})
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, AsyncGenerator
from loguru import logger
import json

# 导入依赖项
from ...dependencies import get_db_manager, get_current_user_optional
from ...services.chat_service import ChatService
from ...models.chat_session import (
    ChatSessionResponse,
    ChatSessionCreateRequest
)
from ...models.chat_message import (
    ChatMessageResponse
)
from ...models.chat import (
    ChatRequest
)

# 创建路由器
router = APIRouter(prefix="/chat", tags=["聊天"])

# 服务实例将在依赖注入中创建


class CreateSessionRequest(BaseModel):
    """
    创建会话请求模型
    """
    title: Optional[str] = Field(None, max_length=200, description="会话标题")
    ai_role_id: str = Field(..., description="AI角色ID")
    system_prompt: Optional[str] = Field(None, max_length=2000, description="系统提示词")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "技术讨论",
                "ai_role_id": "role_tech_expert",
                "system_prompt": "你是一个专业的技术专家，请用专业但易懂的方式回答问题。"
            }
        }


class SendMessageRequest(BaseModel):
    """
    发送消息请求模型
    """
    content: str = Field(..., min_length=1, max_length=4000, description="消息内容")
    message_type: str = Field("text", description="消息类型")
    metadata: Optional[Dict[str, Any]] = Field(None, description="消息元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "你好，请介绍一下Python的特点",
                "message_type": "text",
                "metadata": {"source": "web"}
            }
        }


class ChatResponseModel(BaseModel):
    """
    聊天响应模型
    """
    message: ChatMessageResponse = Field(..., description="用户消息")
    ai_response: ChatMessageResponse = Field(..., description="AI回复")
    session: ChatSessionResponse = Field(..., description="会话信息")


class SessionListResponse(BaseModel):
    """
    会话列表响应模型
    """
    sessions: List[ChatSessionResponse] = Field(..., description="会话列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")


class MessageListResponse(BaseModel):
    """
    消息列表响应模型
    """
    messages: List[ChatMessageResponse] = Field(..., description="消息列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")


@router.post(
    "/sessions",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建聊天会话",
    description="创建新的AI聊天会话"
)
async def create_session(
    request: CreateSessionRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    db = Depends(get_db_manager)
) -> ChatSessionResponse:
    """
    创建聊天会话
    
    Args:
        request: 创建会话请求
        current_user: 当前用户信息(可选)
        db: 数据库客户端
        
    Returns:
        ChatSessionResponse: 会话信息
        
    Raises:
        HTTPException: 创建失败
    """
    user_id = current_user.get("sub") if current_user else None
    logger.info(f"💬 创建聊天会话: 用户={user_id}, 角色={request.ai_role_id}")
    
    try:
        # 创建聊天服务实例
        chat_service = ChatService(db)
        
        # 创建会话数据
        session_data = ChatSessionCreateRequest(
            title=request.title or "新对话",
            ai_role_id=request.ai_role_id
        )
        
        # 创建会话
        from uuid import UUID
        user_uuid = UUID(user_id) if user_id else None
        session = await chat_service.create_session(session_data, user_uuid)
        
        logger.info(f"✅ 聊天会话创建成功: ID={session.id}")
        return session
        
    except Exception as e:
        logger.error(f"❌ 创建聊天会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建会话失败，请稍后重试"
        )


@router.get(
    "/sessions",
    response_model=SessionListResponse,
    summary="获取聊天会话列表",
    description="获取用户的聊天会话列表"
)
async def get_sessions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    db = Depends(get_db_manager)
) -> SessionListResponse:
    """
    获取聊天会话列表
    
    Args:
        page: 页码
        page_size: 每页大小
        current_user: 当前用户信息(可选)
        db: 数据库客户端
        
    Returns:
        SessionListResponse: 会话列表
    """
    user_id = current_user.get("sub") if current_user else None
    logger.debug(f"📋 获取聊天会话列表: 用户={user_id}, 页码={page}")
    
    try:
        # 创建聊天服务实例
        chat_service = ChatService(db)
        
        # 获取会话列表
        from uuid import UUID
        user_uuid = UUID(user_id) if user_id else None
        sessions, total = await chat_service.get_user_sessions(
            user_uuid, page, page_size
        )
        
        return SessionListResponse(
            sessions=sessions,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"❌ 获取聊天会话列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取会话列表失败"
        )


@router.get(
    "/sessions/{session_id}",
    response_model=ChatSessionResponse,
    summary="获取聊天会话详情",
    description="获取指定聊天会话的详细信息"
)
async def get_session(
    session_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    db = Depends(get_db_manager)
) -> ChatSessionResponse:
    """
    获取聊天会话详情
    
    Args:
        session_id: 会话ID
        current_user: 当前用户信息(可选)
        db: 数据库客户端
        
    Returns:
        ChatSessionResponse: 会话详情
        
    Raises:
        HTTPException: 会话不存在或无权限
    """
    user_id = current_user.get("sub") if current_user else None
    logger.debug(f"🔍 获取聊天会话详情: ID={session_id}, 用户={user_id}")
    
    try:
        # 创建聊天服务实例
        chat_service = ChatService(db)
        
        # 获取会话
        from uuid import UUID
        session_uuid = UUID(session_id)
        user_uuid = UUID(user_id) if user_id else None
        session = await chat_service.get_session(session_uuid, user_uuid)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或无权限访问"
            )
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取聊天会话详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取会话详情失败"
        )


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除聊天会话",
    description="删除指定的聊天会话及其所有消息"
)
async def delete_session(
    session_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    db = Depends(get_db_manager)
):
    """
    删除聊天会话
    
    Args:
        session_id: 会话ID
        current_user: 当前用户信息(可选)
        db: 数据库客户端
        
    Raises:
        HTTPException: 删除失败
    """
    user_id = current_user.get("sub") if current_user else None
    logger.info(f"🗑️ 删除聊天会话: ID={session_id}, 用户={user_id}")
    
    try:
        # 创建聊天服务实例
        chat_service = ChatService(db)
        
        # 删除会话
        from uuid import UUID
        session_uuid = UUID(session_id)
        user_uuid = UUID(user_id) if user_id else None
        result = await chat_service.delete_session(session_uuid, user_uuid)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或无权限删除"
            )
        
        logger.info(f"✅ 聊天会话删除成功: ID={session_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除聊天会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除会话失败"
        )


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ChatResponse,
    summary="发送消息",
    description="向指定会话发送消息并获取AI回复"
)
async def send_message(
    session_id: str,
    request: SendMessageRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    db = Depends(get_db_manager)
) -> ChatResponse:
    """
    发送消息
    
    Args:
        session_id: 会话ID
        request: 发送消息请求
        current_user: 当前用户信息(可选)
        db: 数据库客户端
        
    Returns:
        ChatResponse: 聊天响应
        
    Raises:
        HTTPException: 发送失败
    """
    user_id = current_user.get("sub") if current_user else None
    logger.info(f"💬 发送消息: 会话={session_id}, 用户={user_id}")
    
    try:
        # 创建聊天服务实例
        chat_service = ChatService(db)
        
        # 创建聊天请求
        from uuid import UUID
        session_uuid = UUID(session_id)
        user_uuid = UUID(user_id) if user_id else None
        
        chat_request = ChatRequest(
            content=request.content,
            session_id=session_uuid,
            user_id=user_uuid,
            metadata=request.metadata or {}
        )
        
        # 发送消息并获取AI回复
        response = await chat_service.send_message(chat_request)
        
        logger.info(f"✅ 消息发送成功: 会话={session_id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 发送消息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送消息失败，请稍后重试"
        )


@router.post(
    "/sessions/{session_id}/messages/stream",
    summary="流式发送消息",
    description="向指定会话发送消息并获取流式AI回复"
)
async def send_message_stream(
    session_id: str,
    request: SendMessageRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    db = Depends(get_db_manager)
) -> StreamingResponse:
    """
    流式发送消息
    
    Args:
        session_id: 会话ID
        request: 发送消息请求
        current_user: 当前用户信息(可选)
        db: 数据库客户端
        
    Returns:
        StreamingResponse: 流式响应
        
    Raises:
        HTTPException: 发送失败
    """
    user_id = current_user.get("sub") if current_user else None
    logger.info(f"🌊 流式发送消息: 会话={session_id}, 用户={user_id}")
    
    try:
        # 创建聊天服务实例
        chat_service = ChatService(db)
        
        # 验证会话权限
        from uuid import UUID
        session_uuid = UUID(session_id)
        user_uuid = UUID(user_id) if user_id else None
        session = await chat_service.get_session(session_uuid, user_uuid)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或无权限访问"
            )
        
        async def generate_stream() -> AsyncGenerator[str, None]:
            """
            生成流式响应
            """
            try:
                # 创建聊天服务实例
                chat_service = ChatService(db)
                
                # 创建聊天请求
                from uuid import UUID
                session_uuid = UUID(session_id)
                user_uuid = UUID(user_id) if user_id else None
                
                chat_request = ChatRequest(
                    content=request.content,
                    session_id=session_uuid,
                    user_id=user_uuid,
                    metadata=request.metadata or {}
                )
                
                # 发送用户消息确认
                yield f"data: {json.dumps({'type': 'user_message', 'content': request.content}, ensure_ascii=False)}\n\n"
                
                # 流式发送消息并获取AI回复
                async for chunk in chat_service.send_message_stream(chat_request):
                    if chunk.type == "error":
                        yield f"data: {json.dumps({'error': chunk.content}, ensure_ascii=False)}\n\n"
                        return
                    elif chunk.type == "ai_response_start":
                        yield f"data: {json.dumps({'type': 'ai_response_start'}, ensure_ascii=False)}\n\n"
                    elif chunk.type == "ai_response_chunk":
                        yield f"data: {json.dumps({'type': 'ai_response_chunk', 'content': chunk.content}, ensure_ascii=False)}\n\n"
                    elif chunk.type == "ai_response_complete":
                        yield f"data: {json.dumps({'type': 'ai_response_complete', 'message_id': str(chunk.message_id)}, ensure_ascii=False)}\n\n"
                
                logger.info(f"✅ 流式消息发送完成: 会话={session_id}")
                
            except Exception as e:
                logger.error(f"❌ 流式消息生成失败: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'data': {'message': '生成回复失败'}}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 流式发送消息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送消息失败，请稍后重试"
        )


@router.get(
    "/sessions/{session_id}/messages",
    response_model=MessageListResponse,
    summary="获取消息历史",
    description="获取指定会话的消息历史记录"
)
async def get_messages(
    session_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页大小"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    db = Depends(get_db_manager)
) -> MessageListResponse:
    """
    获取消息历史
    
    Args:
        session_id: 会话ID
        page: 页码
        page_size: 每页大小
        current_user: 当前用户信息(可选)
        db: 数据库客户端
        
    Returns:
        MessageListResponse: 消息列表
        
    Raises:
        HTTPException: 获取失败
    """
    user_id = current_user.get("sub") if current_user else None
    logger.debug(f"📜 获取消息历史: 会话={session_id}, 用户={user_id}")
    
    try:
        # 创建聊天服务实例
        chat_service = ChatService(db)
        
        # 获取消息列表
        from uuid import UUID
        session_uuid = UUID(session_id)
        user_uuid = UUID(user_id) if user_id else None
        
        messages, total = await chat_service.get_session_messages_paginated(
            session_uuid, user_uuid, page, page_size
        )
        
        return MessageListResponse(
            messages=messages,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取消息历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取消息历史失败"
        )


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    db = Depends(get_db_manager)
):
    """
    WebSocket聊天端点
    
    Args:
        websocket: WebSocket连接
        session_id: 会话ID
        db: 数据库客户端
    """
    await websocket.accept()
    logger.info(f"🔗 WebSocket连接建立: 会话={session_id}")
    
    # 创建聊天服务实例
    chat_service = ChatService(db)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 验证消息格式
            if "content" not in message_data:
                await websocket.send_text(json.dumps({
                    "error": "消息格式错误"
                }, ensure_ascii=False))
                continue
            
            # 创建聊天请求
            from uuid import UUID
            session_uuid = UUID(session_id)
            user_id = message_data.get("user_id")
            user_uuid = UUID(user_id) if user_id else None
            
            chat_request = ChatRequest(
                content=message_data["content"],
                session_id=session_uuid,
                user_id=user_uuid,
                metadata=message_data.get("metadata", {})
            )
            
            # 发送用户消息确认
            await websocket.send_text(json.dumps({
                "type": "user_message",
                "content": message_data["content"]
            }, ensure_ascii=False))
            
            # 流式发送消息并获取AI回复
            async for chunk in chat_service.send_message_stream(chat_request):
                if chunk.type == "error":
                    await websocket.send_text(json.dumps({
                        "error": chunk.content
                    }, ensure_ascii=False))
                    break
                elif chunk.type == "ai_response_start":
                    await websocket.send_text(json.dumps({
                        "type": "ai_response_start"
                    }, ensure_ascii=False))
                elif chunk.type == "ai_response_chunk":
                    await websocket.send_text(json.dumps({
                        "type": "ai_response_chunk",
                        "content": chunk.content
                    }, ensure_ascii=False))
                elif chunk.type == "ai_response_complete":
                    await websocket.send_text(json.dumps({
                        "type": "ai_response_complete",
                        "message_id": str(chunk.message_id)
                    }, ensure_ascii=False))
            
            logger.info(f"✅ WebSocket消息处理完成: 会话={session_id}")
            
    except Exception as e:
        logger.error(f"❌ WebSocket连接错误: {str(e)}")
        await websocket.close()
    finally:
        logger.info(f"🔌 WebSocket连接关闭: 会话={session_id}")