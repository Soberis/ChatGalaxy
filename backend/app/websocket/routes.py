#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket路由
处理WebSocket连接和实时通信
"""

import json
import uuid
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.security import HTTPBearer
import logging

from ..core.auth import verify_token
from ..services.chat_service import get_chat_service
from ..services.websocket_service import get_websocket_service
from .manager import get_connection_manager

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

router = APIRouter()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: Optional[str] = None
):
    """
    WebSocket连接端点
    
    Args:
        websocket: WebSocket连接对象
        session_id: 聊天会话ID
        token: 认证令牌（可选，访客模式不需要）
    """
    connection_id = str(uuid.uuid4())
    connection_manager = get_connection_manager()
    websocket_service = get_websocket_service()
    chat_service = get_chat_service()
    
    user_id = None
    
    try:
        # 验证用户身份（如果提供了token）
        if token:
            try:
                user_data = verify_token(token)
                user_id = user_data.get("user_id")
                logger.info(f"认证用户连接WebSocket: {user_id}, 会话: {session_id}")
            except Exception as e:
                logger.warning(f"WebSocket认证失败: {str(e)}, 使用访客模式")
        else:
            logger.info(f"访客用户连接WebSocket, 会话: {session_id}")
        
        # 验证会话是否存在
        try:
            session = await chat_service.get_session(session_id, user_id)
            if not session:
                await websocket.close(code=4004, reason="会话不存在")
                return
        except Exception as e:
            logger.error(f"验证会话失败: {str(e)}")
            await websocket.close(code=4003, reason="会话验证失败")
            return
        
        # 建立WebSocket连接
        success = await connection_manager.connect(
            websocket=websocket,
            connection_id=connection_id,
            session_id=session_id,
            user_id=user_id
        )
        
        if not success:
            await websocket.close(code=4001, reason="连接建立失败")
            return
        
        # 注册到WebSocket服务
        await websocket_service.connect(
            connection_id=connection_id,
            websocket=websocket,
            session_id=session_id,
            user_id=user_id
        )
        
        logger.info(f"WebSocket连接成功建立: {connection_id}")
        
        # 消息处理循环
        while True:
            try:
                # 接收消息
                message = await websocket.receive_text()
                logger.debug(f"收到WebSocket消息: {connection_id}, 消息: {message}")
                
                # 解析消息
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "无效的JSON格式",
                        "timestamp": chat_service._get_current_time()
                    }, ensure_ascii=False))
                    continue
                
                # 处理消息
                await websocket_service.handle_message(
                    connection_id=connection_id,
                    message_data=data
                )
                
                # 同时通过连接管理器处理
                await connection_manager.handle_message(connection_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket客户端主动断开连接: {connection_id}")
                break
            except Exception as e:
                logger.error(f"处理WebSocket消息异常: {connection_id}, 错误: {str(e)}")
                try:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "消息处理失败",
                        "error": str(e),
                        "timestamp": chat_service._get_current_time()
                    }, ensure_ascii=False))
                except:
                    break
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket连接断开: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket连接异常: {connection_id}, 错误: {str(e)}")
    finally:
        # 清理连接
        try:
            await websocket_service.disconnect(connection_id)
            await connection_manager.disconnect(connection_id)
            logger.info(f"WebSocket连接清理完成: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket连接清理失败: {connection_id}, 错误: {str(e)}")

@router.get("/ws/stats")
async def get_websocket_stats():
    """
    获取WebSocket连接统计信息
    
    Returns:
        dict: 连接统计信息
    """
    try:
        connection_manager = get_connection_manager()
        websocket_service = get_websocket_service()
        
        return {
            "success": True,
            "data": {
                "total_connections": connection_manager.get_connection_count(),
                "active_sessions": len(connection_manager.session_subscriptions),
                "service_connections": len(websocket_service.connections),
                "heartbeat_tasks": len(connection_manager.heartbeat_tasks)
            }
        }
    except Exception as e:
        logger.error(f"获取WebSocket统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取统计信息失败")

@router.post("/ws/broadcast/{session_id}")
async def broadcast_to_session(
    session_id: str,
    message: dict,
    current_user: dict = Depends(verify_token)
):
    """
    向指定会话广播消息（管理员功能）
    
    Args:
        session_id: 会话ID
        message: 要广播的消息
        current_user: 当前用户信息
        
    Returns:
        dict: 广播结果
    """
    try:
        # 检查用户权限（这里简化处理，实际应该检查管理员权限）
        if not current_user:
            raise HTTPException(status_code=401, detail="未授权")
        
        connection_manager = get_connection_manager()
        
        # 添加系统消息标识
        broadcast_message = {
            "type": "system_broadcast",
            "content": message,
            "timestamp": chat_service._get_current_time(),
            "from": "system"
        }
        
        await connection_manager.broadcast_to_session(session_id, broadcast_message)
        
        return {
            "success": True,
            "message": "消息广播成功",
            "session_id": session_id,
            "connections_count": connection_manager.get_session_connection_count(session_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"广播消息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="广播消息失败")

@router.delete("/ws/connections/{connection_id}")
async def force_disconnect(
    connection_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    强制断开指定连接（管理员功能）
    
    Args:
        connection_id: 连接ID
        current_user: 当前用户信息
        
    Returns:
        dict: 断开结果
    """
    try:
        # 检查用户权限
        if not current_user:
            raise HTTPException(status_code=401, detail="未授权")
        
        connection_manager = get_connection_manager()
        websocket_service = get_websocket_service()
        
        # 检查连接是否存在
        connection_info = connection_manager.get_connection_info(connection_id)
        if not connection_info:
            raise HTTPException(status_code=404, detail="连接不存在")
        
        # 强制断开连接
        await websocket_service.disconnect(connection_id)
        await connection_manager.disconnect(connection_id)
        
        return {
            "success": True,
            "message": "连接已强制断开",
            "connection_id": connection_id,
            "connection_info": connection_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"强制断开连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail="强制断开连接失败")