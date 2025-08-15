#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy WebSocket服务模块

提供WebSocket实时通信功能:
- WebSocket连接管理
- 实时消息推送
- 流式AI响应
- 连接状态管理
- 心跳检测
"""

from typing import Dict, List, Optional, Set, Any
from uuid import UUID
import json
import asyncio
import logging
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

from ..models.chat import ChatRequest, StreamChatResponse
from .chat_service import ChatService
from .auth_service import AuthService


class ConnectionType(Enum):
    """连接类型枚举"""
    AUTHENTICATED = "authenticated"  # 认证用户
    GUEST = "guest"  # 访客用户


class MessageType(Enum):
    """WebSocket消息类型枚举"""
    # 连接管理
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"
    
    # 聊天消息
    CHAT_MESSAGE = "chat_message"
    CHAT_RESPONSE = "chat_response"
    CHAT_STREAM = "chat_stream"
    CHAT_ERROR = "chat_error"
    
    # 会话管理
    SESSION_CREATE = "session_create"
    SESSION_UPDATE = "session_update"
    SESSION_DELETE = "session_delete"
    
    # 系统消息
    SYSTEM_MESSAGE = "system_message"
    ERROR = "error"


class WebSocketConnection:
    """
    WebSocket连接封装类
    
    管理单个WebSocket连接的状态和信息
    """
    
    def __init__(
        self, 
        websocket: WebSocket, 
        connection_id: str,
        connection_type: ConnectionType,
        user_id: Optional[UUID] = None,
        session_token: Optional[str] = None
    ):
        """
        初始化WebSocket连接
        
        Args:
            websocket: WebSocket实例
            connection_id: 连接ID
            connection_type: 连接类型
            user_id: 用户ID（认证用户）
            session_token: 会话令牌（访客用户）
        """
        self.websocket = websocket
        self.connection_id = connection_id
        self.connection_type = connection_type
        self.user_id = user_id
        self.session_token = session_token
        self.connected_at = datetime.utcnow()
        self.last_ping = datetime.utcnow()
        self.is_active = True
        self.subscribed_sessions: Set[str] = set()
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """
        发送消息到客户端
        
        Args:
            message: 消息内容
            
        Returns:
            bool: 发送是否成功
        """
        try:
            if self.is_active:
                await self.websocket.send_text(json.dumps(message, default=str))
                return True
            return False
        except Exception:
            self.is_active = False
            return False
    
    async def close(self, code: int = 1000, reason: str = "Normal closure"):
        """
        关闭WebSocket连接
        
        Args:
            code: 关闭代码
            reason: 关闭原因
        """
        try:
            if self.is_active:
                await self.websocket.close(code=code, reason=reason)
        except Exception:
            pass
        finally:
            self.is_active = False


class WebSocketService:
    """
    WebSocket服务类
    
    管理所有WebSocket连接和实时通信功能
    """
    
    def __init__(
        self, 
        chat_service: ChatService,
        auth_service: AuthService
    ):
        """
        初始化WebSocket服务
        
        Args:
            chat_service: 聊天服务
            auth_service: 认证服务
        """
        self.chat_service = chat_service
        self.auth_service = auth_service
        self.logger = logging.getLogger(__name__)
        
        # 连接管理
        self.connections: Dict[str, WebSocketConnection] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.session_connections: Dict[str, Set[str]] = {}  # session_id -> connection_ids
        
        # 心跳检测任务
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.heartbeat_interval = 30  # 30秒心跳间隔
        self.heartbeat_timeout = 60  # 60秒超时
    
    async def start_service(self):
        """
        启动WebSocket服务
        
        启动心跳检测等后台任务
        """
        if not self.heartbeat_task or self.heartbeat_task.done():
            self.heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
            self.logger.info("WebSocket服务启动成功")
    
    async def stop_service(self):
        """
        停止WebSocket服务
        
        关闭所有连接和后台任务
        """
        # 取消心跳任务
        if self.heartbeat_task and not self.heartbeat_task.done():
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # 关闭所有连接
        for connection in list(self.connections.values()):
            await connection.close(code=1001, reason="Service shutdown")
        
        self.connections.clear()
        self.user_connections.clear()
        self.session_connections.clear()
        
        self.logger.info("WebSocket服务停止成功")
    
    async def connect(
        self, 
        websocket: WebSocket, 
        connection_id: str,
        token: Optional[str] = None,
        session_token: Optional[str] = None
    ) -> Optional[WebSocketConnection]:
        """
        建立WebSocket连接
        
        Args:
            websocket: WebSocket实例
            connection_id: 连接ID
            token: 认证令牌（可选）
            session_token: 会话令牌（访客模式）
            
        Returns:
            Optional[WebSocketConnection]: 连接对象
        """
        try:
            await websocket.accept()
            
            # 确定连接类型和用户信息
            connection_type = ConnectionType.GUEST
            user_id = None
            
            if token:
                try:
                    # 验证认证令牌
                    user = await self.auth_service.get_current_user(token)
                    if user:
                        connection_type = ConnectionType.AUTHENTICATED
                        user_id = user.id
                        self.logger.info(f"认证用户连接: {user.username} ({connection_id})")
                    else:
                        self.logger.warning(f"无效的认证令牌: {connection_id}")
                except Exception as e:
                    self.logger.warning(f"令牌验证失败: {str(e)}")
            
            if connection_type == ConnectionType.GUEST:
                self.logger.info(f"访客用户连接: {connection_id}")
            
            # 创建连接对象
            connection = WebSocketConnection(
                websocket=websocket,
                connection_id=connection_id,
                connection_type=connection_type,
                user_id=user_id,
                session_token=session_token
            )
            
            # 注册连接
            self.connections[connection_id] = connection
            
            # 按用户分组连接
            if user_id:
                user_key = str(user_id)
                if user_key not in self.user_connections:
                    self.user_connections[user_key] = set()
                self.user_connections[user_key].add(connection_id)
            
            # 发送连接成功消息
            await connection.send_message({
                "type": MessageType.CONNECT.value,
                "connection_id": connection_id,
                "connection_type": connection_type.value,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.logger.info(f"WebSocket连接建立成功: {connection_id}")
            return connection
            
        except Exception as e:
            self.logger.error(f"WebSocket连接失败: {str(e)}")
            try:
                await websocket.close(code=1011, reason="Connection failed")
            except Exception:
                pass
            return None
    
    async def disconnect(self, connection_id: str):
        """
        断开WebSocket连接
        
        Args:
            connection_id: 连接ID
        """
        try:
            connection = self.connections.get(connection_id)
            if not connection:
                return
            
            # 从用户连接组中移除
            if connection.user_id:
                user_key = str(connection.user_id)
                if user_key in self.user_connections:
                    self.user_connections[user_key].discard(connection_id)
                    if not self.user_connections[user_key]:
                        del self.user_connections[user_key]
            
            # 从会话连接组中移除
            for session_id in list(connection.subscribed_sessions):
                if session_id in self.session_connections:
                    self.session_connections[session_id].discard(connection_id)
                    if not self.session_connections[session_id]:
                        del self.session_connections[session_id]
            
            # 关闭连接
            await connection.close()
            
            # 移除连接记录
            del self.connections[connection_id]
            
            self.logger.info(f"WebSocket连接断开: {connection_id}")
            
        except Exception as e:
            self.logger.error(f"断开WebSocket连接失败: {str(e)}")
    
    async def handle_message(
        self, 
        connection_id: str, 
        message: Dict[str, Any]
    ):
        """
        处理WebSocket消息
        
        Args:
            connection_id: 连接ID
            message: 消息内容
        """
        try:
            connection = self.connections.get(connection_id)
            if not connection or not connection.is_active:
                return
            
            message_type = message.get("type")
            
            if message_type == MessageType.PING.value:
                await self._handle_ping(connection)
            elif message_type == MessageType.CHAT_MESSAGE.value:
                await self._handle_chat_message(connection, message)
            elif message_type == MessageType.SESSION_CREATE.value:
                await self._handle_session_create(connection, message)
            elif message_type == MessageType.SESSION_UPDATE.value:
                await self._handle_session_update(connection, message)
            elif message_type == MessageType.SESSION_DELETE.value:
                await self._handle_session_delete(connection, message)
            else:
                await connection.send_message({
                    "type": MessageType.ERROR.value,
                    "error": "Unknown message type",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
        except Exception as e:
            self.logger.error(f"处理WebSocket消息失败: {str(e)}")
            await self._send_error(connection_id, f"消息处理失败: {str(e)}")
    
    async def subscribe_session(
        self, 
        connection_id: str, 
        session_id: str
    ) -> bool:
        """
        订阅会话消息
        
        Args:
            connection_id: 连接ID
            session_id: 会话ID
            
        Returns:
            bool: 订阅是否成功
        """
        try:
            connection = self.connections.get(connection_id)
            if not connection:
                return False
            
            # 添加到会话连接组
            if session_id not in self.session_connections:
                self.session_connections[session_id] = set()
            self.session_connections[session_id].add(connection_id)
            
            # 添加到连接的订阅列表
            connection.subscribed_sessions.add(session_id)
            
            self.logger.info(f"连接 {connection_id} 订阅会话 {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"订阅会话失败: {str(e)}")
            return False
    
    async def unsubscribe_session(
        self, 
        connection_id: str, 
        session_id: str
    ) -> bool:
        """
        取消订阅会话消息
        
        Args:
            connection_id: 连接ID
            session_id: 会话ID
            
        Returns:
            bool: 取消订阅是否成功
        """
        try:
            connection = self.connections.get(connection_id)
            if not connection:
                return False
            
            # 从会话连接组中移除
            if session_id in self.session_connections:
                self.session_connections[session_id].discard(connection_id)
                if not self.session_connections[session_id]:
                    del self.session_connections[session_id]
            
            # 从连接的订阅列表中移除
            connection.subscribed_sessions.discard(session_id)
            
            self.logger.info(f"连接 {connection_id} 取消订阅会话 {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"取消订阅会话失败: {str(e)}")
            return False
    
    async def broadcast_to_session(
        self, 
        session_id: str, 
        message: Dict[str, Any],
        exclude_connection: Optional[str] = None
    ):
        """
        向会话的所有连接广播消息
        
        Args:
            session_id: 会话ID
            message: 消息内容
            exclude_connection: 排除的连接ID
        """
        try:
            connection_ids = self.session_connections.get(session_id, set())
            
            for connection_id in connection_ids:
                if exclude_connection and connection_id == exclude_connection:
                    continue
                
                connection = self.connections.get(connection_id)
                if connection and connection.is_active:
                    await connection.send_message(message)
                    
        except Exception as e:
            self.logger.error(f"会话广播失败: {str(e)}")
    
    async def broadcast_to_user(
        self, 
        user_id: UUID, 
        message: Dict[str, Any]
    ):
        """
        向用户的所有连接广播消息
        
        Args:
            user_id: 用户ID
            message: 消息内容
        """
        try:
            user_key = str(user_id)
            connection_ids = self.user_connections.get(user_key, set())
            
            for connection_id in connection_ids:
                connection = self.connections.get(connection_id)
                if connection and connection.is_active:
                    await connection.send_message(message)
                    
        except Exception as e:
            self.logger.error(f"用户广播失败: {str(e)}")
    
    async def _handle_ping(self, connection: WebSocketConnection):
        """
        处理心跳ping消息
        
        Args:
            connection: WebSocket连接
        """
        connection.last_ping = datetime.utcnow()
        await connection.send_message({
            "type": MessageType.PONG.value,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _handle_chat_message(
        self, 
        connection: WebSocketConnection, 
        message: Dict[str, Any]
    ):
        """
        处理聊天消息
        
        Args:
            connection: WebSocket连接
            message: 消息内容
        """
        try:
            # 解析聊天请求
            chat_data = message.get("data", {})
            chat_request = ChatRequest(**chat_data)
            
            # 订阅会话（如果尚未订阅）
            session_id = str(chat_request.session_id)
            await self.subscribe_session(connection.connection_id, session_id)
            
            # 检查是否为流式模式
            if chat_request.mode and chat_request.mode.value == "STREAM":
                # 流式响应
                async for stream_response in self.chat_service.stream_message(
                    chat_request,
                    connection.user_id,
                    connection.session_token
                ):
                    # 发送流式响应到所有订阅的连接
                    stream_message = {
                        "type": MessageType.CHAT_STREAM.value,
                        "data": {
                            "session_id": str(stream_response.session_id),
                            "message_id": str(stream_response.message_id),
                            "content": stream_response.content,
                            "is_complete": stream_response.is_complete,
                            "tokens_used": stream_response.tokens_used,
                            "timestamp": stream_response.timestamp.isoformat()
                        }
                    }
                    
                    await self.broadcast_to_session(
                        session_id, 
                        stream_message
                    )
            else:
                # 普通响应
                chat_response = await self.chat_service.send_message(
                    chat_request,
                    connection.user_id,
                    connection.session_token
                )
                
                # 发送响应到所有订阅的连接
                response_message = {
                    "type": MessageType.CHAT_RESPONSE.value,
                    "data": {
                        "session_id": str(chat_response.session_id),
                        "user_message_id": str(chat_response.user_message_id),
                        "ai_message_id": str(chat_response.ai_message_id),
                        "ai_role_name": chat_response.ai_role_name,
                        "content": chat_response.content,
                        "tokens_used": chat_response.tokens_used,
                        "response_time": chat_response.response_time,
                        "metadata": chat_response.metadata,
                        "timestamp": chat_response.timestamp.isoformat()
                    }
                }
                
                await self.broadcast_to_session(
                    session_id, 
                    response_message
                )
                
        except Exception as e:
            self.logger.error(f"处理聊天消息失败: {str(e)}")
            await connection.send_message({
                "type": MessageType.CHAT_ERROR.value,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def _handle_session_create(
        self, 
        connection: WebSocketConnection, 
        message: Dict[str, Any]
    ):
        """
        处理会话创建
        
        Args:
            connection: WebSocket连接
            message: 消息内容
        """
        try:
            from ..models.chat import ChatSessionCreate as ChatSessionCreateRequest
            
            session_data = ChatSessionCreateRequest(**message.get("data", {}))
            
            # 创建会话
            session_response = await self.chat_service.create_session(
                session_data,
                connection.user_id
            )
            
            # 自动订阅新会话
            await self.subscribe_session(
                connection.connection_id, 
                str(session_response.session_id)
            )
            
            # 发送创建成功响应
            await connection.send_message({
                "type": MessageType.SESSION_CREATE.value,
                "data": {
                    "session_id": str(session_response.session_id),
                    "session_token": session_response.session_token,
                    "title": session_response.title,
                    "ai_role": {
                        "id": str(session_response.ai_role.id),
                        "name": session_response.ai_role.name,
                        "avatar_url": session_response.ai_role.avatar_url
                    },
                    "created_at": session_response.created_at.isoformat()
                },
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"处理会话创建失败: {str(e)}")
            await connection.send_message({
                "type": MessageType.ERROR.value,
                "error": f"会话创建失败: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def _handle_session_update(
        self, 
        connection: WebSocketConnection, 
        message: Dict[str, Any]
    ):
        """
        处理会话更新
        
        Args:
            connection: WebSocket连接
            message: 消息内容
        """
        try:
            from ..models.chat_session import ChatSessionUpdate
            
            data = message.get("data", {})
            session_id = UUID(data.get("session_id"))
            update_data = ChatSessionUpdate(**data.get("update", {}))
            
            # 更新会话
            updated_session = await self.chat_service.update_session(
                session_id,
                update_data,
                connection.user_id,
                connection.session_token
            )
            
            if updated_session:
                # 广播更新到所有订阅的连接
                update_message = {
                    "type": MessageType.SESSION_UPDATE.value,
                    "data": {
                        "session_id": str(updated_session.id),
                        "title": updated_session.title,
                        "is_active": updated_session.is_active,
                        "session_status": updated_session.session_status.value,
                        "updated_at": updated_session.updated_at.isoformat()
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await self.broadcast_to_session(
                    str(session_id), 
                    update_message
                )
            else:
                await connection.send_message({
                    "type": MessageType.ERROR.value,
                    "error": "会话更新失败",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
        except Exception as e:
            self.logger.error(f"处理会话更新失败: {str(e)}")
            await connection.send_message({
                "type": MessageType.ERROR.value,
                "error": f"会话更新失败: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def _handle_session_delete(
        self, 
        connection: WebSocketConnection, 
        message: Dict[str, Any]
    ):
        """
        处理会话删除
        
        Args:
            connection: WebSocket连接
            message: 消息内容
        """
        try:
            data = message.get("data", {})
            session_id = UUID(data.get("session_id"))
            
            # 删除会话
            success = await self.chat_service.delete_session(
                session_id,
                connection.user_id,
                connection.session_token
            )
            
            if success:
                # 广播删除消息到所有订阅的连接
                delete_message = {
                    "type": MessageType.SESSION_DELETE.value,
                    "data": {
                        "session_id": str(session_id)
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await self.broadcast_to_session(
                    str(session_id), 
                    delete_message
                )
                
                # 清理会话连接
                if str(session_id) in self.session_connections:
                    del self.session_connections[str(session_id)]
            else:
                await connection.send_message({
                    "type": MessageType.ERROR.value,
                    "error": "会话删除失败",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
        except Exception as e:
            self.logger.error(f"处理会话删除失败: {str(e)}")
            await connection.send_message({
                "type": MessageType.ERROR.value,
                "error": f"会话删除失败: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def _send_error(
        self, 
        connection_id: str, 
        error_message: str
    ):
        """
        发送错误消息
        
        Args:
            connection_id: 连接ID
            error_message: 错误消息
        """
        connection = self.connections.get(connection_id)
        if connection:
            await connection.send_message({
                "type": MessageType.ERROR.value,
                "error": error_message,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def _heartbeat_monitor(self):
        """
        心跳监控任务
        
        定期检查连接状态，清理超时连接
        """
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                current_time = datetime.utcnow()
                timeout_connections = []
                
                # 检查超时连接
                for connection_id, connection in self.connections.items():
                    time_since_ping = (current_time - connection.last_ping).total_seconds()
                    
                    if time_since_ping > self.heartbeat_timeout:
                        timeout_connections.append(connection_id)
                        self.logger.warning(f"连接超时: {connection_id}")
                
                # 清理超时连接
                for connection_id in timeout_connections:
                    await self.disconnect(connection_id)
                
                if timeout_connections:
                    self.logger.info(f"清理了 {len(timeout_connections)} 个超时连接")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"心跳监控异常: {str(e)}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """
        获取连接统计信息
        
        Returns:
            Dict[str, Any]: 连接统计数据
        """
        try:
            total_connections = len(self.connections)
            authenticated_connections = sum(
                1 for conn in self.connections.values() 
                if conn.connection_type == ConnectionType.AUTHENTICATED
            )
            guest_connections = total_connections - authenticated_connections
            active_sessions = len(self.session_connections)
            
            return {
                "total_connections": total_connections,
                "authenticated_connections": authenticated_connections,
                "guest_connections": guest_connections,
                "active_sessions": active_sessions,
                "unique_users": len(self.user_connections),
                "heartbeat_interval": self.heartbeat_interval,
                "heartbeat_timeout": self.heartbeat_timeout
            }
            
        except Exception as e:
            self.logger.error(f"获取连接统计失败: {str(e)}")
            return {}
    
    async def send_system_message(
        self, 
        message: str, 
        target_type: str = "all",
        target_id: Optional[str] = None
    ):
        """
        发送系统消息
        
        Args:
            message: 系统消息内容
            target_type: 目标类型 (all, user, session, connection)
            target_id: 目标ID
        """
        try:
            system_message = {
                "type": MessageType.SYSTEM_MESSAGE.value,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if target_type == "all":
                # 广播给所有连接
                for connection in self.connections.values():
                    if connection.is_active:
                        await connection.send_message(system_message)
            
            elif target_type == "user" and target_id:
                # 发送给特定用户
                await self.broadcast_to_user(UUID(target_id), system_message)
            
            elif target_type == "session" and target_id:
                # 发送给特定会话
                await self.broadcast_to_session(target_id, system_message)
            
            elif target_type == "connection" and target_id:
                # 发送给特定连接
                connection = self.connections.get(target_id)
                if connection and connection.is_active:
                    await connection.send_message(system_message)
            
            self.logger.info(f"系统消息发送成功: {target_type}:{target_id}")
            
        except Exception as e:
            self.logger.error(f"发送系统消息失败: {str(e)}")