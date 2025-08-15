#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy AI角色服务模块

提供AI角色管理相关的业务逻辑:
- AI角色的创建、查询、更新和删除
- 角色统计和使用分析
- 预设角色初始化
- 角色权限管理
"""

from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import logging

from ..core.database import DatabaseManager
from ..models.ai_role import (
    AIRole, AIRoleCreate, AIRoleUpdate, AIRoleResponse, 
    AIRoleStats, AIRoleType
)


class AIRoleService:
    """
    AI角色服务类
    
    提供AI角色管理的核心业务逻辑
    """
    
    def __init__(self, db: DatabaseManager):
        """
        初始化AI角色服务
        
        Args:
            db: 数据库管理器
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    async def create_role(self, role_data: AIRoleCreate) -> AIRoleResponse:
        """
        创建AI角色
        
        Args:
            role_data: 角色创建数据
            
        Returns:
            AIRoleResponse: 创建的角色信息
            
        Raises:
            ValueError: 角色名称已存在
            Exception: 创建失败
        """
        try:
            # 检查角色名称是否已存在
            existing_role = await self.get_role_by_name(role_data.name)
            if existing_role:
                raise ValueError(f"角色名称 '{role_data.name}' 已存在")
            
            # 生成角色ID
            role_id = uuid4()
            
            # 准备数据库数据
            db_data = {
                "id": str(role_id),
                "name": role_data.name,
                "description": role_data.description,
                "role_type": role_data.role_type.value,
                "avatar_url": role_data.avatar_url,
                "personality": role_data.personality,
                "system_prompt": role_data.system_prompt,
                "greeting_message": role_data.greeting_message,
                "is_active": role_data.is_active,
                "is_default": role_data.is_default,
                "usage_count": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # 如果设置为默认角色，先取消其他默认角色
            if role_data.is_default:
                await self._clear_default_roles(role_data.role_type)
            
            # 插入数据库
            result = await self.db.insert("ai_roles", db_data)
            if not result:
                raise Exception("角色创建失败")
            
            # 获取创建的角色
            created_role = await self.get_role_by_id(role_id)
            if not created_role:
                raise Exception("获取创建的角色失败")
            
            self.logger.info(f"AI角色创建成功: {role_data.name} ({role_id})")
            return created_role
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"AI角色创建失败: {str(e)}")
            raise Exception(f"角色创建失败: {str(e)}")
    
    async def get_role_by_id(self, role_id: UUID) -> Optional[AIRoleResponse]:
        """
        根据ID获取AI角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            Optional[AIRoleResponse]: 角色信息，不存在则返回None
        """
        try:
            result = await self.db.select(
                "ai_roles",
                filters={"id": str(role_id)},
                limit=1
            )
            
            if not result:
                return None
            
            role_data = result[0]
            return self._convert_to_response(role_data)
            
        except Exception as e:
            self.logger.error(f"获取AI角色失败: {str(e)}")
            return None
    
    async def get_role_by_name(self, name: str) -> Optional[AIRoleResponse]:
        """
        根据名称获取AI角色
        
        Args:
            name: 角色名称
            
        Returns:
            Optional[AIRoleResponse]: 角色信息，不存在则返回None
        """
        try:
            result = await self.db.select(
                "ai_roles",
                filters={"name": name},
                limit=1
            )
            
            if not result:
                return None
            
            role_data = result[0]
            return self._convert_to_response(role_data)
            
        except Exception as e:
            self.logger.error(f"根据名称获取AI角色失败: {str(e)}")
            return None
    
    async def get_roles(
        self, 
        role_type: Optional[AIRoleType] = None,
        is_active: Optional[bool] = None,
        is_default: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AIRoleResponse]:
        """
        获取AI角色列表
        
        Args:
            role_type: 角色类型过滤
            is_active: 激活状态过滤
            is_default: 默认角色过滤
            skip: 跳过数量
            limit: 限制数量
            
        Returns:
            List[AIRoleResponse]: 角色列表
        """
        try:
            # 构建过滤条件
            filters = {}
            if role_type is not None:
                filters["role_type"] = role_type.value
            if is_active is not None:
                filters["is_active"] = is_active
            if is_default is not None:
                filters["is_default"] = is_default
            
            # 查询数据库
            result = await self.db.select(
                "ai_roles",
                filters=filters,
                order_by="created_at DESC",
                offset=skip,
                limit=limit
            )
            
            # 转换为响应模型
            roles = []
            for role_data in result:
                role_response = self._convert_to_response(role_data)
                if role_response:
                    roles.append(role_response)
            
            return roles
            
        except Exception as e:
            self.logger.error(f"获取AI角色列表失败: {str(e)}")
            return []
    
    async def get_default_roles(self) -> List[AIRoleResponse]:
        """
        获取所有默认角色
        
        Returns:
            List[AIRoleResponse]: 默认角色列表
        """
        return await self.get_roles(is_default=True, is_active=True)
    
    async def get_roles_by_type(self, role_type: AIRoleType) -> List[AIRoleResponse]:
        """
        根据类型获取角色列表
        
        Args:
            role_type: 角色类型
            
        Returns:
            List[AIRoleResponse]: 角色列表
        """
        return await self.get_roles(role_type=role_type, is_active=True)
    
    async def update_role(self, role_id: UUID, role_data: AIRoleUpdate) -> Optional[AIRoleResponse]:
        """
        更新AI角色
        
        Args:
            role_id: 角色ID
            role_data: 更新数据
            
        Returns:
            Optional[AIRoleResponse]: 更新后的角色信息
            
        Raises:
            ValueError: 角色不存在或名称冲突
            Exception: 更新失败
        """
        try:
            # 检查角色是否存在
            existing_role = await self.get_role_by_id(role_id)
            if not existing_role:
                raise ValueError("角色不存在")
            
            # 准备更新数据
            update_data = {"updated_at": datetime.utcnow().isoformat()}
            
            # 检查名称是否冲突
            if role_data.name is not None:
                name_conflict = await self.get_role_by_name(role_data.name)
                if name_conflict and name_conflict.id != role_id:
                    raise ValueError(f"角色名称 '{role_data.name}' 已存在")
                update_data["name"] = role_data.name
            
            # 更新其他字段
            if role_data.description is not None:
                update_data["description"] = role_data.description
            if role_data.role_type is not None:
                update_data["role_type"] = role_data.role_type.value
            if role_data.avatar_url is not None:
                update_data["avatar_url"] = role_data.avatar_url
            if role_data.personality is not None:
                update_data["personality"] = role_data.personality
            if role_data.system_prompt is not None:
                update_data["system_prompt"] = role_data.system_prompt
            if role_data.greeting_message is not None:
                update_data["greeting_message"] = role_data.greeting_message
            if role_data.is_active is not None:
                update_data["is_active"] = role_data.is_active
            if role_data.is_default is not None:
                update_data["is_default"] = role_data.is_default
                # 如果设置为默认角色，先取消其他默认角色
                if role_data.is_default:
                    role_type = role_data.role_type or existing_role.role_type
                    await self._clear_default_roles(role_type, exclude_id=role_id)
            
            # 执行更新
            result = await self.db.update(
                "ai_roles",
                update_data,
                filters={"id": str(role_id)}
            )
            
            if not result:
                raise Exception("角色更新失败")
            
            # 获取更新后的角色
            updated_role = await self.get_role_by_id(role_id)
            
            self.logger.info(f"AI角色更新成功: {role_id}")
            return updated_role
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"AI角色更新失败: {str(e)}")
            raise Exception(f"角色更新失败: {str(e)}")
    
    async def delete_role(self, role_id: UUID) -> bool:
        """
        删除AI角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            ValueError: 角色不存在或正在使用中
        """
        try:
            # 检查角色是否存在
            existing_role = await self.get_role_by_id(role_id)
            if not existing_role:
                raise ValueError("角色不存在")
            
            # 检查是否有活跃的聊天会话使用此角色
            active_sessions = await self.db.select(
                "chat_sessions",
                filters={"ai_role_id": str(role_id), "is_active": True},
                limit=1
            )
            
            if active_sessions:
                raise ValueError("角色正在使用中，无法删除")
            
            # 执行删除
            result = await self.db.delete(
                "ai_roles",
                filters={"id": str(role_id)}
            )
            
            if not result:
                raise Exception("角色删除失败")
            
            self.logger.info(f"AI角色删除成功: {role_id}")
            return True
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"AI角色删除失败: {str(e)}")
            raise Exception(f"角色删除失败: {str(e)}")
    
    async def increment_usage_count(self, role_id: UUID) -> bool:
        """
        增加角色使用次数
        
        Args:
            role_id: 角色ID
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 获取当前使用次数
            result = await self.db.select(
                "ai_roles",
                filters={"id": str(role_id)},
                columns=["usage_count"],
                limit=1
            )
            
            if not result:
                return False
            
            current_count = result[0]["usage_count"] or 0
            
            # 更新使用次数
            update_result = await self.db.update(
                "ai_roles",
                {
                    "usage_count": current_count + 1,
                    "updated_at": datetime.utcnow().isoformat()
                },
                filters={"id": str(role_id)}
            )
            
            return bool(update_result)
            
        except Exception as e:
            self.logger.error(f"更新角色使用次数失败: {str(e)}")
            return False
    
    async def get_role_stats(self, role_id: UUID) -> Optional[AIRoleStats]:
        """
        获取角色统计信息
        
        Args:
            role_id: 角色ID
            
        Returns:
            Optional[AIRoleStats]: 角色统计信息
        """
        try:
            # 获取角色基本信息
            role = await self.get_role_by_id(role_id)
            if not role:
                return None
            
            # 获取会话统计
            session_stats = await self.db.select(
                "chat_sessions",
                filters={"ai_role_id": str(role_id)},
                columns=["COUNT(*) as total_sessions", "SUM(message_count) as total_messages", "SUM(total_tokens) as total_tokens"]
            )
            
            total_sessions = session_stats[0]["total_sessions"] if session_stats else 0
            total_messages = session_stats[0]["total_messages"] if session_stats else 0
            total_tokens = session_stats[0]["total_tokens"] if session_stats else 0
            
            # 获取活跃会话数
            active_sessions = await self.db.select(
                "chat_sessions",
                filters={"ai_role_id": str(role_id), "is_active": True},
                columns=["COUNT(*) as active_sessions"]
            )
            
            active_session_count = active_sessions[0]["active_sessions"] if active_sessions else 0
            
            return AIRoleStats(
                role_id=role_id,
                role_name=role.name,
                usage_count=role.usage_count,
                total_sessions=total_sessions,
                active_sessions=active_session_count,
                total_messages=total_messages,
                total_tokens=total_tokens,
                created_at=role.created_at,
                last_used_at=datetime.utcnow()  # 这里可以从最近的会话获取
            )
            
        except Exception as e:
            self.logger.error(f"获取角色统计失败: {str(e)}")
            return None
    
    async def initialize_default_roles(self) -> bool:
        """
        初始化默认AI角色
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 检查是否已经初始化
            existing_roles = await self.get_default_roles()
            if existing_roles:
                self.logger.info("默认角色已存在，跳过初始化")
                return True
            
            # 定义默认角色
            default_roles = [
                {
                    "name": "智能助手",
                    "description": "专业的AI助手，能够回答各种问题并提供帮助",
                    "role_type": AIRoleType.ASSISTANT,
                    "avatar_url": "/avatars/assistant.png",
                    "personality": "专业、友善、乐于助人",
                    "system_prompt": "你是一个专业的AI助手，能够回答用户的各种问题。请保持友善、专业的态度，提供准确和有用的信息。",
                    "greeting_message": "你好！我是你的智能助手，有什么可以帮助你的吗？",
                    "is_active": True,
                    "is_default": True
                },
                {
                    "name": "创意作家",
                    "description": "富有创意的写作助手，擅长创作故事、诗歌和文案",
                    "role_type": AIRoleType.CREATIVE,
                    "avatar_url": "/avatars/writer.png",
                    "personality": "富有想象力、文艺、充满创意",
                    "system_prompt": "你是一位富有创意的作家，擅长创作各种文学作品。请发挥你的想象力，创作出生动有趣的内容。",
                    "greeting_message": "嗨！我是你的创意伙伴，让我们一起创作出精彩的作品吧！",
                    "is_active": True,
                    "is_default": True
                },
                {
                    "name": "技术专家",
                    "description": "专业的技术顾问，精通编程、系统架构和技术解决方案",
                    "role_type": AIRoleType.TECHNICAL,
                    "avatar_url": "/avatars/developer.png",
                    "personality": "严谨、专业、逻辑清晰",
                    "system_prompt": "你是一位经验丰富的技术专家，精通各种编程语言和技术栈。请提供准确的技术建议和解决方案。",
                    "greeting_message": "你好！我是技术专家，准备好解决你的技术问题了！",
                    "is_active": True,
                    "is_default": True
                },
                {
                    "name": "轻松聊天",
                    "description": "轻松愉快的聊天伙伴，适合日常闲聊和娱乐",
                    "role_type": AIRoleType.CASUAL,
                    "avatar_url": "/avatars/casual.png",
                    "personality": "轻松、幽默、平易近人",
                    "system_prompt": "你是一个轻松愉快的聊天伙伴，喜欢和用户进行轻松的对话。请保持友好和幽默的态度。",
                    "greeting_message": "嘿！很高兴见到你，我们聊点什么有趣的吧！",
                    "is_active": True,
                    "is_default": True
                }
            ]
            
            # 创建默认角色
            created_count = 0
            for role_data in default_roles:
                try:
                    role_create = AIRoleCreate(**role_data)
                    await self.create_role(role_create)
                    created_count += 1
                except Exception as e:
                    self.logger.error(f"创建默认角色失败: {role_data['name']} - {str(e)}")
            
            self.logger.info(f"默认角色初始化完成，成功创建 {created_count} 个角色")
            return created_count > 0
            
        except Exception as e:
            self.logger.error(f"初始化默认角色失败: {str(e)}")
            return False
    
    async def _clear_default_roles(self, role_type: AIRoleType, exclude_id: Optional[UUID] = None) -> bool:
        """
        清除指定类型的默认角色标记
        
        Args:
            role_type: 角色类型
            exclude_id: 排除的角色ID
            
        Returns:
            bool: 操作是否成功
        """
        try:
            filters = {"role_type": role_type.value, "is_default": True}
            if exclude_id:
                # 这里需要使用NOT条件，简化处理
                roles = await self.db.select(
                    "ai_roles",
                    filters={"role_type": role_type.value, "is_default": True}
                )
                
                for role in roles:
                    if role["id"] != str(exclude_id):
                        await self.db.update(
                            "ai_roles",
                            {"is_default": False, "updated_at": datetime.utcnow().isoformat()},
                            filters={"id": role["id"]}
                        )
            else:
                await self.db.update(
                    "ai_roles",
                    {"is_default": False, "updated_at": datetime.utcnow().isoformat()},
                    filters=filters
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"清除默认角色标记失败: {str(e)}")
            return False
    
    def _convert_to_response(self, role_data: Dict[str, Any]) -> Optional[AIRoleResponse]:
        """
        将数据库数据转换为响应模型
        
        Args:
            role_data: 数据库数据
            
        Returns:
            Optional[AIRoleResponse]: 响应模型
        """
        try:
            return AIRoleResponse(
                id=UUID(role_data["id"]),
                name=role_data["name"],
                description=role_data["description"],
                role_type=AIRoleType(role_data["role_type"]),
                avatar_url=role_data["avatar_url"],
                personality=role_data["personality"],
                system_prompt=role_data["system_prompt"],
                greeting_message=role_data["greeting_message"],
                is_active=role_data["is_active"],
                is_default=role_data["is_default"],
                usage_count=role_data["usage_count"] or 0,
                created_at=datetime.fromisoformat(role_data["created_at"]),
                updated_at=datetime.fromisoformat(role_data["updated_at"])
            )
        except Exception as e:
            self.logger.error(f"转换角色数据失败: {str(e)}")
            return None