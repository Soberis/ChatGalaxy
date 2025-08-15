#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 聊天服务模块

提供聊天相关的业务逻辑:
- 聊天会话管理
- 消息发送和接收
- AI对话集成
- 聊天历史记录
- 流式响应处理
"""

from typing import List, Optional, Dict, Any, AsyncGenerator
from uuid import UUID, uuid4
from datetime import datetime
import logging
import json
import asyncio
from fastapi import HTTPException

from ..core.database import DatabaseManager
from ..core.ai_client import AIClient, get_ai_client, AIResponse, StreamChunk
from ..models.chat_session import (
    ChatSession, ChatSessionCreate, ChatSessionUpdate, 
    ChatSessionResponse, SessionStatus
)
from ..models.chat_message import (
    ChatMessage, ChatMessageCreate, ChatMessageResponse,
    MessageType, MessageStatus
)
from ..models.chat import (
    ChatRequest, ChatResponse, StreamChatResponse,
    ChatHistory, ChatContext, ChatSessionCreate as ChatSessionCreateRequest,
    ChatSessionResponse as ChatSessionCreateResponse, MessageRole
)
from ..models.chat_message import MessageStatus
from .ai_role_service import AIRoleService
from .user_service import UserService


class ChatService:
    """
    聊天服务类
    
    提供聊天会话和消息管理的核心业务逻辑
    """
    
    def __init__(
        self, 
        db: DatabaseManager, 
        ai_client: Optional[AIClient] = None,
        ai_role_service: Optional[AIRoleService] = None,
        user_service: Optional[UserService] = None
    ):
        """
        初始化聊天服务
        
        Args:
            db: 数据库管理器
            ai_client: AI客户端（可选）
            ai_role_service: AI角色服务（可选）
            user_service: 用户服务（可选）
        """
        self.db = db
        self.ai_client = ai_client
        self.ai_role_service = ai_role_service or AIRoleService(db)
        self.user_service = user_service or UserService(db)
        self.logger = logging.getLogger(__name__)
    
    async def create_session(
        self, 
        session_data: ChatSessionCreateRequest,
        user_id: Optional[UUID] = None
    ) -> ChatSessionCreateResponse:
        """
        创建聊天会话
        
        Args:
            session_data: 会话创建数据
            user_id: 用户ID（可选，访客模式为None）
            
        Returns:
            ChatSessionCreateResponse: 创建的会话信息
            
        Raises:
            ValueError: 角色不存在或参数无效
            Exception: 创建失败
        """
        try:
            # 验证AI角色
            ai_role = await self.ai_role_service.get_role_by_id(session_data.ai_role_id)
            if not ai_role or not ai_role.is_active:
                raise ValueError("AI角色不存在或已停用")
            
            # 生成会话ID和令牌
            session_id = uuid4()
            session_token = None
            
            # 访客模式需要生成会话令牌
            if user_id is None:
                import secrets
                session_token = secrets.token_urlsafe(32)
            
            # 准备数据库数据
            db_data = {
                "id": str(session_id),
                "title": session_data.title or f"与{ai_role.name}的对话",
                "ai_role_id": str(session_data.ai_role_id),
                "user_id": str(user_id) if user_id else None,
                "session_token": session_token,
                "is_active": True,
                "session_status": SessionStatus.ACTIVE.value,
                "message_count": 0,
                "total_tokens": 0,
                "last_message_at": None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # 插入数据库
            result = await self.db.insert("chat_sessions", db_data)
            if not result:
                raise Exception("会话创建失败")
            
            # 增加角色使用次数
            await self.ai_role_service.increment_usage_count(session_data.ai_role_id)
            
            # 发送欢迎消息
            if ai_role.greeting_message:
                await self._create_system_message(
                    session_id,
                    ai_role.greeting_message,
                    session_data.ai_role_id
                )
            
            self.logger.info(f"聊天会话创建成功: {session_id}")
            
            return ChatSessionCreateResponse(
                session_id=session_id,
                session_token=session_token,
                ai_role=ai_role,
                title=db_data["title"],
                created_at=datetime.fromisoformat(db_data["created_at"])
            )
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"聊天会话创建失败: {str(e)}")
            raise Exception(f"会话创建失败: {str(e)}")
    
    async def get_session(
        self, 
        session_id: UUID,
        user_id: Optional[UUID] = None,
        session_token: Optional[str] = None
    ) -> Optional[ChatSessionResponse]:
        """
        获取聊天会话
        
        Args:
            session_id: 会话ID
            user_id: 用户ID（可选）
            session_token: 会话令牌（访客模式必需）
            
        Returns:
            Optional[ChatSessionResponse]: 会话信息
        """
        try:
            # 构建查询条件
            filters = {"id": str(session_id)}
            
            # 根据用户类型添加验证条件
            if user_id:
                filters["user_id"] = str(user_id)
            else:
                if not session_token:
                    return None
                filters["session_token"] = session_token
                filters["user_id"] = None  # 确保是访客会话
            
            # 查询会话
            result = await self.db.select(
                "chat_sessions",
                filters=filters,
                limit=1
            )
            
            if not result:
                return None
            
            session_data = result[0]
            
            # 获取AI角色信息
            ai_role = await self.ai_role_service.get_role_by_id(
                UUID(session_data["ai_role_id"])
            )
            
            if not ai_role:
                return None
            
            return ChatSessionResponse(
                id=UUID(session_data["id"]),
                title=session_data["title"],
                ai_role_id=UUID(session_data["ai_role_id"]),
                ai_role_name=ai_role.name,
                ai_role_avatar=ai_role.avatar_url,
                user_id=UUID(session_data["user_id"]) if session_data["user_id"] else None,
                session_token=session_data["session_token"],
                is_active=session_data["is_active"],
                session_status=SessionStatus(session_data["session_status"]),
                message_count=session_data["message_count"] or 0,
                total_tokens=session_data["total_tokens"] or 0,
                last_message_at=datetime.fromisoformat(session_data["last_message_at"]) if session_data["last_message_at"] else None,
                created_at=datetime.fromisoformat(session_data["created_at"]),
                updated_at=datetime.fromisoformat(session_data["updated_at"])
            )
            
        except Exception as e:
            self.logger.error(f"获取聊天会话失败: {str(e)}")
            return None
    
    async def get_user_sessions(
        self, 
        user_id: UUID,
        status: Optional[SessionStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ChatSessionResponse]:
        """
        获取用户的聊天会话列表
        
        Args:
            user_id: 用户ID
            status: 会话状态过滤
            skip: 跳过数量
            limit: 限制数量
            
        Returns:
            List[ChatSessionResponse]: 会话列表
        """
        try:
            # 构建过滤条件
            filters = {"user_id": str(user_id)}
            if status:
                filters["session_status"] = status.value
            
            # 查询会话
            result = await self.db.select(
                "chat_sessions",
                filters=filters,
                order_by="updated_at DESC",
                offset=skip,
                limit=limit
            )
            
            # 转换为响应模型
            sessions = []
            for session_data in result:
                # 获取AI角色信息
                ai_role = await self.ai_role_service.get_role_by_id(
                    UUID(session_data["ai_role_id"])
                )
                
                if ai_role:
                    session_response = ChatSessionResponse(
                        id=UUID(session_data["id"]),
                        title=session_data["title"],
                        ai_role_id=UUID(session_data["ai_role_id"]),
                        ai_role_name=ai_role.name,
                        ai_role_avatar=ai_role.avatar_url,
                        user_id=UUID(session_data["user_id"]) if session_data["user_id"] else None,
                        session_token=session_data["session_token"],
                        is_active=session_data["is_active"],
                        session_status=SessionStatus(session_data["session_status"]),
                        message_count=session_data["message_count"] or 0,
                        total_tokens=session_data["total_tokens"] or 0,
                        last_message_at=datetime.fromisoformat(session_data["last_message_at"]) if session_data["last_message_at"] else None,
                        created_at=datetime.fromisoformat(session_data["created_at"]),
                        updated_at=datetime.fromisoformat(session_data["updated_at"])
                    )
                    sessions.append(session_response)
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"获取用户会话列表失败: {str(e)}")
            return []
    
    async def send_message(
        self, 
        chat_request: ChatRequest,
        user_id: Optional[UUID] = None,
        session_token: Optional[str] = None
    ) -> ChatResponse:
        """
        发送聊天消息
        
        Args:
            chat_request: 聊天请求
            user_id: 用户ID（可选）
            session_token: 会话令牌（访客模式必需）
            
        Returns:
            ChatResponse: 聊天响应
            
        Raises:
            ValueError: 会话不存在或参数无效
            Exception: 发送失败
        """
        try:
            # 验证会话
            session = await self.get_session(
                chat_request.session_id, user_id, session_token
            )
            if not session:
                raise ValueError("会话不存在或无权限访问")
            
            # 获取AI角色
            ai_role = await self.ai_role_service.get_role_by_id(session.ai_role_id)
            if not ai_role:
                raise ValueError("AI角色不存在")
            
            # 创建用户消息
            user_message_id = await self._create_user_message(
                chat_request.session_id,
                chat_request.message,
                user_id
            )
            
            # 准备AI对话上下文
            context = await self._build_chat_context(
                chat_request.session_id,
                ai_role,
                chat_request.context_messages
            )
            
            # 获取AI客户端
            if not self.ai_client:
                self.ai_client = await get_ai_client()
            
            # 准备上下文消息
            context_messages = []
            if context.messages:
                for msg in context.messages:
                    context_messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # 调用AI服务生成响应
            ai_response = await self.ai_client.generate_response(
                content=chat_request.message,
                ai_role=ai_role,
                context_messages=context_messages,
                temperature=chat_request.temperature or 0.7,
                max_tokens=chat_request.max_tokens or 2000
            )
            
            # 创建AI响应消息
            ai_message_id = await self._create_ai_message(
                chat_request.session_id,
                ai_response.content,
                chat_request.ai_role_id,
                ai_response.tokens_used,
                {"model": ai_response.model, "finish_reason": ai_response.finish_reason}
            )
            
            # 更新会话统计
            await self._update_session_stats(
                chat_request.session_id,
                message_count_increment=2,  # 用户消息 + AI消息
                token_count_increment=ai_response.tokens_used
            )
            
            self.logger.info(f"消息发送成功: {chat_request.session_id}")
            
            return ChatResponse(
                session_id=chat_request.session_id,
                user_message_id=user_message_id,
                ai_message_id=ai_message_id,
                ai_role_name=ai_role.name,
                content=ai_response.content,
                tokens_used=ai_response.tokens_used,
                response_time=ai_response.response_time,
                metadata={
                    "model": ai_response.model,
                    "finish_reason": ai_response.finish_reason,
                    "temperature": chat_request.temperature
                },
                timestamp=datetime.utcnow()
            )
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"发送消息失败: {str(e)}")
            raise Exception(f"消息发送失败: {str(e)}")
    
    async def stream_message(
        self, 
        chat_request: ChatRequest,
        user_id: Optional[str] = None,
        session_token: Optional[str] = None
    ) -> AsyncGenerator[StreamChatResponse, None]:
        """
        发送流式聊天消息
        
        Args:
            chat_request: 聊天请求
            user_id: 用户ID（可选）
            session_token: 会话令牌（可选）
            
        Yields:
            StreamChatResponse: 流式聊天响应
            
        Raises:
            ValueError: 参数错误
            HTTPException: 会话不存在或无权限
        """
        try:
            # 验证会话
            session = await self._validate_session(chat_request.session_id, user_id, session_token)
            if not session:
                raise HTTPException(status_code=404, detail="会话不存在")
            
            # 获取AI角色
            ai_role = await self.ai_role_service.get_role(session.ai_role_id)
            if not ai_role:
                raise HTTPException(status_code=404, detail="AI角色不存在")
            
            # 创建用户消息记录
            user_message = await self._create_message(
                session_id=chat_request.session_id,
                role=MessageRole.USER,
                content=chat_request.message,
                message_type=MessageType.TEXT
            )
            
            # 获取对话上下文
            context = await self._build_context(
                session_id=chat_request.session_id,
                ai_role=ai_role,
                limit=10
            )
            
            # 获取AI客户端
            if not self.ai_client:
                self.ai_client = await get_ai_client()
            
            # 准备上下文消息
            context_messages = []
            if context.messages:
                for msg in context.messages:
                    context_messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # 创建AI消息记录（初始为空）
            ai_message = await self._create_message(
                session_id=chat_request.session_id,
                role=MessageRole.ASSISTANT,
                content="",
                message_type=MessageType.TEXT
            )
            
            # 流式生成AI响应
            full_content = ""
            token_count = 0
            
            async for chunk in self.ai_client.generate_stream_response(
                content=chat_request.message,
                ai_role=ai_role,
                context_messages=context_messages,
                temperature=chat_request.temperature or 0.7,
                max_tokens=chat_request.max_tokens or 2000
            ):
                if chunk.content:
                    full_content += chunk.content
                    token_count += chunk.token_count or 0
                    
                    # 返回流式响应
                    yield StreamChatResponse(
                        session_id=chat_request.session_id,
                        message_id=ai_message.id,
                        content=chunk.content,
                        is_complete=chunk.is_final,
                        token_count=chunk.token_count or 0,
                        timestamp=datetime.utcnow()
                    )
            
            # 更新AI消息记录
            await self._update_message_content(ai_message.id, full_content)
            
            # 更新会话统计
            await self._update_session_stats(
                session_id=chat_request.session_id,
                message_count=2,  # 用户消息 + AI消息
                token_count=token_count
            )
            
            self.logger.info(
                f"流式消息处理完成 - 会话: {chat_request.session_id}, "
                f"用户: {user_id or 'guest'}, Token: {token_count}"
            )
            
        except Exception as e:
            self.logger.error(f"流式消息处理失败: {str(e)}")
            # 返回错误响应
            yield StreamChatResponse(
                session_id=chat_request.session_id,
                message_id="",
                content=f"处理消息时发生错误: {str(e)}",
                is_complete=True,
                token_count=0,
                timestamp=datetime.utcnow(),
                error=str(e)
            )
            raise
    
    async def get_chat_history(
        self, 
        session_id: UUID,
        user_id: Optional[UUID] = None,
        session_token: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Optional[ChatHistory]:
        """
        获取聊天历史记录
        
        Args:
            session_id: 会话ID
            user_id: 用户ID（可选）
            session_token: 会话令牌（访客模式必需）
            skip: 跳过数量
            limit: 限制数量
            
        Returns:
            Optional[ChatHistory]: 聊天历史
        """
        try:
            # 验证会话权限
            session = await self.get_session(session_id, user_id, session_token)
            if not session:
                return None
            
            # 获取消息列表
            messages_data = await self.db.select(
                "chat_messages",
                filters={"session_id": str(session_id)},
                order_by="created_at ASC",
                offset=skip,
                limit=limit
            )
            
            # 转换为响应模型
            messages = []
            for msg_data in messages_data:
                # 获取AI角色信息（如果是AI消息）
                ai_role_name = None
                ai_role_avatar = None
                
                if msg_data["ai_role_id"]:
                    ai_role = await self.ai_role_service.get_role_by_id(
                        UUID(msg_data["ai_role_id"])
                    )
                    if ai_role:
                        ai_role_name = ai_role.name
                        ai_role_avatar = ai_role.avatar_url
                
                message_response = ChatMessageResponse(
                    id=UUID(msg_data["id"]),
                    session_id=UUID(msg_data["session_id"]),
                    content=msg_data["content"],
                    message_type=MessageType(msg_data["message_type"]),
                    ai_role_id=UUID(msg_data["ai_role_id"]) if msg_data["ai_role_id"] else None,
                    ai_role_name=ai_role_name,
                    ai_role_avatar=ai_role_avatar,
                    parent_message_id=UUID(msg_data["parent_message_id"]) if msg_data["parent_message_id"] else None,
                    status=MessageStatus(msg_data["status"]),
                    token_count=msg_data["token_count"] or 0,
                    metadata=json.loads(msg_data["metadata"]) if msg_data["metadata"] else {},
                    created_at=datetime.fromisoformat(msg_data["created_at"]),
                    updated_at=datetime.fromisoformat(msg_data["updated_at"])
                )
                messages.append(message_response)
            
            return ChatHistory(
                session_id=session_id,
                messages=messages,
                total_messages=session.message_count,
                total_tokens=session.total_tokens,
                session_info=session
            )
            
        except Exception as e:
            self.logger.error(f"获取聊天历史失败: {str(e)}")
            return None
    
    async def _update_message_content(self, message_id: str, content: str) -> None:
        """
        更新消息内容
        
        Args:
            message_id: 消息ID
            content: 新内容
        """
        try:
            query = """
                UPDATE chat_messages 
                SET content = $1, updated_at = NOW()
                WHERE id = $2
            """
            await self.db.execute(query, content, message_id)
            
        except Exception as e:
            self.logger.error(f"更新消息内容失败: {str(e)}")
            raise
    
    async def _validate_session(
        self, 
        session_id: UUID, 
        user_id: Optional[str] = None, 
        session_token: Optional[str] = None
    ) -> Optional[ChatSessionResponse]:
        """
        验证会话权限
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            session_token: 会话令牌
            
        Returns:
            Optional[ChatSessionResponse]: 会话信息
        """
        return await self.get_session(
            session_id, 
            UUID(user_id) if user_id else None, 
            session_token
        )
    
    async def _create_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        message_type: MessageType
    ) -> ChatMessageResponse:
        """
        创建消息记录
        
        Args:
            session_id: 会话ID
            role: 消息角色
            content: 消息内容
            message_type: 消息类型
            
        Returns:
            ChatMessageResponse: 创建的消息
        """
        message_id = uuid4()
        
        message_data = {
                "id": str(message_id),
                "session_id": str(session_id),
                "content": content,
                "message_type": message_type.value,
                "role_id": None,
                "parent_id": None,
                "status": MessageStatus.COMPLETED.value,
                "tokens_used": 0,
                "metadata": json.dumps({}),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        
        await self.db.insert("chat_messages", message_data)
        
        return ChatMessageResponse(
            id=message_id,
            session_id=session_id,
            parent_id=None,
            content=content,
            message_type=message_type,
            role_id=None,
            status=MessageStatus.COMPLETED,
            tokens_used=0,
            metadata={},
            created_at=datetime.utcnow(),
            role_name=None,
            role_avatar=None
        )
    
    async def _build_context(
        self,
        session_id: UUID,
        ai_role,
        limit: int = 10
    ) -> ChatContext:
        """
        构建对话上下文
        
        Args:
            session_id: 会话ID
            ai_role: AI角色
            limit: 消息数量限制
            
        Returns:
            ChatContext: 对话上下文
        """
        try:
            # 获取最近的消息历史
            recent_messages = await self.db.select(
                "chat_messages",
                filters={"session_id": str(session_id)},
                order_by="created_at DESC",
                limit=limit
            )
            
            # 构建消息列表
            messages = []
            
            # 添加历史消息（按时间正序）
            for msg_data in reversed(recent_messages):
                if msg_data["message_type"] == MessageType.USER.value:
                    messages.append({
                        "role": "user",
                        "content": msg_data["content"]
                    })
                elif msg_data["message_type"] == MessageType.AI.value:
                    messages.append({
                        "role": "assistant",
                        "content": msg_data["content"]
                    })
            
            return ChatContext(
                system_prompt=ai_role.system_prompt,
                messages=messages
            )
            
        except Exception as e:
            self.logger.error(f"构建对话上下文失败: {str(e)}")
            return ChatContext(
                system_prompt=ai_role.system_prompt,
                messages=[]
            )
    
    async def _update_session_stats(
        self, 
        session_id: str, 
        message_count: int = 0, 
        token_count: int = 0
    ) -> None:
        """
        更新会话统计信息
        
        Args:
            session_id: 会话ID
            message_count: 增加的消息数量
            token_count: 增加的token数量
        """
        try:
            query = """
                UPDATE chat_sessions 
                SET 
                    message_count = message_count + $1,
                    token_count = token_count + $2,
                    last_message_at = NOW(),
                    updated_at = NOW()
                WHERE id = $3
            """
            await self.db.execute(query, message_count, token_count, session_id)
            
        except Exception as e:
            self.logger.error(f"更新会话统计失败: {str(e)}")
            raise
    
    async def update_session(
        self, 
        session_id: UUID,
        update_data: ChatSessionUpdate,
        user_id: Optional[UUID] = None,
        session_token: Optional[str] = None
    ) -> Optional[ChatSessionResponse]:
        """
        更新聊天会话
        
        Args:
            session_id: 会话ID
            update_data: 更新数据
            user_id: 用户ID（可选）
            session_token: 会话令牌（访客模式必需）
            
        Returns:
            Optional[ChatSessionResponse]: 更新后的会话信息
        """
        try:
            # 验证会话权限
            session = await self.get_session(session_id, user_id, session_token)
            if not session:
                return None
            
            # 准备更新数据
            db_update = {"updated_at": datetime.utcnow().isoformat()}
            
            if update_data.title is not None:
                db_update["title"] = update_data.title
            if update_data.is_active is not None:
                db_update["is_active"] = update_data.is_active
            if update_data.session_status is not None:
                db_update["session_status"] = update_data.session_status.value
            
            # 执行更新
            result = await self.db.update(
                "chat_sessions",
                db_update,
                filters={"id": str(session_id)}
            )
            
            if not result:
                return None
            
            # 返回更新后的会话
            return await self.get_session(session_id, user_id, session_token)
            
        except Exception as e:
            self.logger.error(f"更新聊天会话失败: {str(e)}")
            return None
    
    async def delete_session(
        self, 
        session_id: UUID,
        user_id: Optional[UUID] = None,
        session_token: Optional[str] = None
    ) -> bool:
        """
        删除聊天会话
        
        Args:
            session_id: 会话ID
            user_id: 用户ID（可选）
            session_token: 会话令牌（访客模式必需）
            
        Returns:
            bool: 删除是否成功
        """
        try:
            # 验证会话权限
            session = await self.get_session(session_id, user_id, session_token)
            if not session:
                return False
            
            # 删除会话消息
            await self.db.delete(
                "chat_messages",
                filters={"session_id": str(session_id)}
            )
            
            # 删除会话
            result = await self.db.delete(
                "chat_sessions",
                filters={"id": str(session_id)}
            )
            
            self.logger.info(f"聊天会话删除成功: {session_id}")
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"删除聊天会话失败: {str(e)}")
            return False
    
    async def _create_user_message(
        self, 
        session_id: UUID, 
        content: str, 
        user_id: Optional[UUID] = None
    ) -> UUID:
        """
        创建用户消息
        
        Args:
            session_id: 会话ID
            content: 消息内容
            user_id: 用户ID
            
        Returns:
            UUID: 消息ID
        """
        message_id = uuid4()
        
        message_data = {
            "id": str(message_id),
            "session_id": str(session_id),
            "content": content,
            "message_type": MessageType.USER.value,
            "role_id": None,
            "parent_id": None,
            "status": MessageStatus.COMPLETED.value,
            "tokens_used": len(content.split()),  # 简单的token估算
            "metadata": json.dumps({"user_id": str(user_id) if user_id else None}),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await self.db.insert("chat_messages", message_data)
        return message_id
    
    async def _create_ai_message(
        self, 
        session_id: UUID, 
        content: str, 
        ai_role_id: UUID,
        token_count: int = 0,
        metadata: Dict[str, Any] = None,
        status: MessageStatus = MessageStatus.COMPLETED
    ) -> UUID:
        """
        创建AI消息
        
        Args:
            session_id: 会话ID
            content: 消息内容
            ai_role_id: AI角色ID
            token_count: token数量
            metadata: 元数据
            status: 消息状态
            
        Returns:
            UUID: 消息ID
        """
        message_id = uuid4()
        
        message_data = {
            "id": str(message_id),
            "session_id": str(session_id),
            "content": content,
            "message_type": MessageType.AI.value,
            "role_id": str(ai_role_id),
            "parent_id": None,
            "status": status.value,
            "tokens_used": token_count,
            "metadata": json.dumps(metadata or {}),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await self.db.insert("chat_messages", message_data)
        return message_id
    
    async def _create_system_message(
        self, 
        session_id: UUID, 
        content: str, 
        ai_role_id: UUID
    ) -> UUID:
        """
        创建系统消息
        
        Args:
            session_id: 会话ID
            content: 消息内容
            ai_role_id: AI角色ID
            
        Returns:
            UUID: 消息ID
        """
        message_id = uuid4()
        
        message_data = {
            "id": str(message_id),
            "session_id": str(session_id),
            "content": content,
            "message_type": MessageType.SYSTEM.value,
            "role_id": str(ai_role_id),
            "parent_id": None,
            "status": MessageStatus.COMPLETED.value,
            "tokens_used": 0,
            "metadata": json.dumps({"type": "greeting"}),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await self.db.insert("chat_messages", message_data)
        
        # 更新会话消息计数
        await self._update_session_stats(session_id, message_count_increment=1)
        
        return message_id
    
    async def _update_ai_message(
        self, 
        message_id: UUID, 
        content: str, 
        token_count: int,
        metadata: Dict[str, Any],
        status: MessageStatus
    ) -> bool:
        """
        更新AI消息
        
        Args:
            message_id: 消息ID
            content: 消息内容
            token_count: token数量
            metadata: 元数据
            status: 消息状态
            
        Returns:
            bool: 更新是否成功
        """
        try:
            result = await self.db.update(
                "chat_messages",
                {
                    "content": content,
                    "tokens_used": token_count,
                    "metadata": json.dumps(metadata),
                    "status": status.value,
                    "updated_at": datetime.utcnow().isoformat()
                },
                filters={"id": str(message_id)}
            )
            return bool(result)
        except Exception as e:
            self.logger.error(f"更新AI消息失败: {str(e)}")
            return False
    
    async def _update_session_stats(
        self, 
        session_id: UUID, 
        message_count_increment: int = 0,
        token_count_increment: int = 0
    ) -> bool:
        """
        更新会话统计信息
        
        Args:
            session_id: 会话ID
            message_count_increment: 消息数增量
            token_count_increment: token数增量
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 获取当前统计
            result = await self.db.select(
                "chat_sessions",
                filters={"id": str(session_id)},
                columns=["message_count", "total_tokens"],
                limit=1
            )
            
            if not result:
                return False
            
            current_data = result[0]
            new_message_count = (current_data["message_count"] or 0) + message_count_increment
            new_token_count = (current_data["total_tokens"] or 0) + token_count_increment
            
            # 更新统计
            update_result = await self.db.update(
                "chat_sessions",
                {
                    "message_count": new_message_count,
                    "total_tokens": new_token_count,
                    "last_message_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                filters={"id": str(session_id)}
            )
            
            return bool(update_result)
            
        except Exception as e:
            self.logger.error(f"更新会话统计失败: {str(e)}")
            return False
    
    async def _build_chat_context(
        self, 
        session_id: UUID, 
        ai_role, 
        context_messages: Optional[List[Dict[str, Any]]] = None
    ) -> ChatContext:
        """
        构建聊天上下文
        
        Args:
            session_id: 会话ID
            ai_role: AI角色
            context_messages: 上下文消息
            
        Returns:
            ChatContext: 聊天上下文
        """
        try:
            # 获取最近的消息历史
            recent_messages = await self.db.select(
                "chat_messages",
                filters={"session_id": str(session_id)},
                order_by="created_at DESC",
                limit=10  # 最近10条消息
            )
            
            # 构建消息列表
            messages = []
            
            # 添加历史消息（按时间正序）
            for msg_data in reversed(recent_messages):
                if msg_data["message_type"] == MessageType.USER.value:
                    messages.append({
                        "role": "user",
                        "content": msg_data["content"]
                    })
                elif msg_data["message_type"] == MessageType.AI.value:
                    messages.append({
                        "role": "assistant",
                        "content": msg_data["content"]
                    })
            
            # 添加自定义上下文消息
            if context_messages:
                messages.extend(context_messages)
            
            return ChatContext(
                system_prompt=ai_role.system_prompt,
                messages=messages
            )
            
        except Exception as e:
            self.logger.error(f"构建聊天上下文失败: {str(e)}")
            return ChatContext(
                system_prompt=ai_role.system_prompt,
                messages=[]
            )