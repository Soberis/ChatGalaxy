#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket连接管理器
处理WebSocket连接的生命周期管理、消息广播和会话订阅
"""

import json
import asyncio
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    WebSocket连接管理器
    负责管理所有WebSocket连接，支持会话订阅和消息广播
    """
    
    def __init__(self):
        # 活跃连接字典：connection_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # 会话订阅字典：session_id -> Set[connection_id]
        self.session_subscriptions: Dict[str, Set[str]] = {}
        # 连接元数据：connection_id -> metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        # 心跳任务字典：connection_id -> asyncio.Task
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str, 
                     session_id: str, user_id: Optional[str] = None) -> bool:
        """
        建立WebSocket连接
        
        Args:
            websocket: WebSocket连接对象
            connection_id: 连接唯一标识
            session_id: 聊天会话ID
            user_id: 用户ID（可选，访客模式为None）
            
        Returns:
            bool: 连接是否成功建立
        """
        try:
            await websocket.accept()
            
            # 存储连接信息
            self.active_connections[connection_id] = websocket
            self.connection_metadata[connection_id] = {
                "session_id": session_id,
                "user_id": user_id,
                "connected_at": datetime.now(),
                "last_heartbeat": datetime.now()
            }
            
            # 订阅会话
            if session_id not in self.session_subscriptions:
                self.session_subscriptions[session_id] = set()
            self.session_subscriptions[session_id].add(connection_id)
            
            # 启动心跳检测
            self.heartbeat_tasks[connection_id] = asyncio.create_task(
                self._heartbeat_loop(connection_id)
            )
            
            logger.info(f"WebSocket连接已建立: {connection_id}, 会话: {session_id}, 用户: {user_id}")
            
            # 发送连接确认消息
            await self.send_personal_message(connection_id, {
                "type": "connection_established",
                "connection_id": connection_id,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"WebSocket连接建立失败: {connection_id}, 错误: {str(e)}")
            return False
    
    async def disconnect(self, connection_id: str):
        """
        断开WebSocket连接
        
        Args:
            connection_id: 连接唯一标识
        """
        try:
            # 取消心跳任务
            if connection_id in self.heartbeat_tasks:
                self.heartbeat_tasks[connection_id].cancel()
                del self.heartbeat_tasks[connection_id]
            
            # 获取连接元数据
            metadata = self.connection_metadata.get(connection_id, {})
            session_id = metadata.get("session_id")
            
            # 从会话订阅中移除
            if session_id and session_id in self.session_subscriptions:
                self.session_subscriptions[session_id].discard(connection_id)
                if not self.session_subscriptions[session_id]:
                    del self.session_subscriptions[session_id]
            
            # 清理连接信息
            self.active_connections.pop(connection_id, None)
            self.connection_metadata.pop(connection_id, None)
            
            logger.info(f"WebSocket连接已断开: {connection_id}, 会话: {session_id}")
            
        except Exception as e:
            logger.error(f"WebSocket连接断开处理失败: {connection_id}, 错误: {str(e)}")
    
    async def send_personal_message(self, connection_id: str, message: Dict[str, Any]):
        """
        发送个人消息
        
        Args:
            connection_id: 连接唯一标识
            message: 消息内容
        """
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"发送个人消息失败: {connection_id}, 错误: {str(e)}")
                await self.disconnect(connection_id)
    
    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any], 
                                  exclude_connection: Optional[str] = None):
        """
        向会话中的所有连接广播消息
        
        Args:
            session_id: 会话ID
            message: 消息内容
            exclude_connection: 排除的连接ID（可选）
        """
        if session_id in self.session_subscriptions:
            connection_ids = self.session_subscriptions[session_id].copy()
            
            for connection_id in connection_ids:
                if exclude_connection and connection_id == exclude_connection:
                    continue
                    
                await self.send_personal_message(connection_id, message)
    
    async def handle_message(self, connection_id: str, message: str):
        """
        处理接收到的WebSocket消息
        
        Args:
            connection_id: 连接唯一标识
            message: 接收到的消息
        """
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "heartbeat":
                # 更新心跳时间
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id]["last_heartbeat"] = datetime.now()
                
                # 回复心跳确认
                await self.send_personal_message(connection_id, {
                    "type": "heartbeat_ack",
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message_type == "ping":
                # 回复pong
                await self.send_personal_message(connection_id, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
            else:
                logger.warning(f"未知消息类型: {message_type}, 连接: {connection_id}")
                
        except json.JSONDecodeError:
            logger.error(f"无效的JSON消息: {connection_id}, 消息: {message}")
        except Exception as e:
            logger.error(f"处理WebSocket消息失败: {connection_id}, 错误: {str(e)}")
    
    async def _heartbeat_loop(self, connection_id: str):
        """
        心跳检测循环
        
        Args:
            connection_id: 连接唯一标识
        """
        try:
            while connection_id in self.active_connections:
                await asyncio.sleep(30)  # 每30秒检查一次
                
                if connection_id not in self.connection_metadata:
                    break
                
                metadata = self.connection_metadata[connection_id]
                last_heartbeat = metadata.get("last_heartbeat")
                
                if last_heartbeat:
                    # 检查是否超过60秒没有心跳
                    time_diff = (datetime.now() - last_heartbeat).total_seconds()
                    if time_diff > 60:
                        logger.warning(f"连接心跳超时: {connection_id}, 超时时间: {time_diff}秒")
                        await self.disconnect(connection_id)
                        break
                
                # 发送心跳请求
                await self.send_personal_message(connection_id, {
                    "type": "heartbeat_request",
                    "timestamp": datetime.now().isoformat()
                })
                
        except asyncio.CancelledError:
            logger.info(f"心跳检测任务已取消: {connection_id}")
        except Exception as e:
            logger.error(f"心跳检测循环异常: {connection_id}, 错误: {str(e)}")
    
    def get_connection_count(self) -> int:
        """
        获取活跃连接数量
        
        Returns:
            int: 活跃连接数量
        """
        return len(self.active_connections)
    
    def get_session_connection_count(self, session_id: str) -> int:
        """
        获取指定会话的连接数量
        
        Args:
            session_id: 会话ID
            
        Returns:
            int: 会话连接数量
        """
        return len(self.session_subscriptions.get(session_id, set()))
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """
        获取连接信息
        
        Args:
            connection_id: 连接唯一标识
            
        Returns:
            Optional[Dict[str, Any]]: 连接信息
        """
        return self.connection_metadata.get(connection_id)

# 全局WebSocket连接管理器实例
connection_manager = ConnectionManager()

def get_connection_manager() -> ConnectionManager:
    """
    获取WebSocket连接管理器实例
    
    Returns:
        ConnectionManager: 连接管理器实例
    """
    return connection_manager