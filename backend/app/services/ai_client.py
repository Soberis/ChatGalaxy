#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy AI客户端服务模块

提供AI服务集成功能:
- 阿里通义千问API集成
- 流式响应处理
- 对话上下文管理
- 角色系统集成
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from uuid import UUID
import httpx
from pydantic import BaseModel
import logging

from ..config import get_settings
from ..models.ai_role import AIRole
from ..services.ai_role_service import AIRoleService
from ..core.database import DatabaseManager


class AIResponse(BaseModel):
    """
    AI响应数据模型
    """
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    response_time: float
    

class StreamChunk(BaseModel):
    """
    流式响应数据块
    """
    content: str
    is_final: bool = False
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None


class AIClient:
    """
    AI客户端类
    
    提供与AI服务的交互功能
    """
    
    def __init__(self, db: DatabaseManager):
        """
        初始化AI客户端
        
        Args:
            db: 数据库管理器
        """
        self.db = db
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        self.ai_role_service = AIRoleService(db)
        
        # 通义千问API配置
        self.qwen_api_key = self.settings.qwen_api_key
        self.qwen_model = self.settings.qwen_model
        self.qwen_max_tokens = self.settings.qwen_max_tokens
        self.qwen_temperature = self.settings.qwen_temperature
        
        # API端点
        self.qwen_api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        # HTTP客户端
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0),
            headers={
                "Authorization": f"Bearer {self.qwen_api_key}",
                "Content-Type": "application/json",
                "X-DashScope-SSE": "enable"  # 启用流式响应
            }
        )
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        ai_role_id: Optional[UUID] = None,
        stream: bool = False
    ) -> AIResponse:
        """
        生成AI响应
        
        Args:
            messages: 对话消息列表
            ai_role_id: AI角色ID（可选）
            stream: 是否使用流式响应
            
        Returns:
            AIResponse: AI响应结果
            
        Raises:
            Exception: API调用失败
        """
        try:
            start_time = time.time()
            
            # 获取AI角色信息
            ai_role = None
            if ai_role_id:
                ai_role = await self.ai_role_service.get_role_by_id(ai_role_id)
            
            # 构建请求消息
            request_messages = await self._build_request_messages(messages, ai_role)
            
            # 构建请求参数
            request_data = {
                "model": self.qwen_model,
                "input": {
                    "messages": request_messages
                },
                "parameters": {
                    "max_tokens": self.qwen_max_tokens,
                    "temperature": self.qwen_temperature,
                    "top_p": 0.8,
                    "repetition_penalty": 1.1,
                    "incremental_output": stream
                }
            }
            
            self.logger.info(f"发送AI请求: model={self.qwen_model}, messages={len(request_messages)}")
            
            if stream:
                return await self._generate_stream_response(request_data, start_time)
            else:
                return await self._generate_single_response(request_data, start_time)
                
        except Exception as e:
            self.logger.error(f"AI响应生成失败: {str(e)}")
            raise Exception(f"AI服务调用失败: {str(e)}")
    
    async def generate_stream_response(
        self,
        messages: List[Dict[str, str]],
        ai_role_id: Optional[UUID] = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        生成流式AI响应
        
        Args:
            messages: 对话消息列表
            ai_role_id: AI角色ID（可选）
            
        Yields:
            StreamChunk: 流式响应数据块
        """
        try:
            # 获取AI角色信息
            ai_role = None
            if ai_role_id:
                ai_role = await self.ai_role_service.get_role_by_id(ai_role_id)
            
            # 构建请求消息
            request_messages = await self._build_request_messages(messages, ai_role)
            
            # 构建请求参数
            request_data = {
                "model": self.qwen_model,
                "input": {
                    "messages": request_messages
                },
                "parameters": {
                    "max_tokens": self.qwen_max_tokens,
                    "temperature": self.qwen_temperature,
                    "top_p": 0.8,
                    "repetition_penalty": 1.1,
                    "incremental_output": True
                }
            }
            
            self.logger.info(f"发送流式AI请求: model={self.qwen_model}")
            
            # 发送流式请求
            async with self.http_client.stream(
                "POST",
                self.qwen_api_url,
                json=request_data
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"API请求失败: {response.status_code} - {error_text.decode()}")
                
                full_content = ""
                tokens_used = 0
                finish_reason = "stop"
                
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    if line.startswith("data: "):
                        data_str = line[6:]
                        
                        if data_str.strip() == "[DONE]":
                            # 发送最终块
                            yield StreamChunk(
                                content="",
                                is_final=True,
                                tokens_used=tokens_used,
                                finish_reason=finish_reason
                            )
                            break
                        
                        try:
                            data = json.loads(data_str)
                            
                            if "output" in data:
                                output = data["output"]
                                
                                if "text" in output:
                                    chunk_content = output["text"]
                                    full_content += chunk_content
                                    
                                    # 发送内容块
                                    yield StreamChunk(
                                        content=chunk_content,
                                        is_final=False
                                    )
                                
                                if "finish_reason" in output:
                                    finish_reason = output["finish_reason"]
                            
                            if "usage" in data:
                                usage = data["usage"]
                                if "total_tokens" in usage:
                                    tokens_used = usage["total_tokens"]
                                    
                        except json.JSONDecodeError as e:
                            self.logger.warning(f"解析流式响应失败: {e}")
                            continue
                
        except Exception as e:
            self.logger.error(f"流式AI响应生成失败: {str(e)}")
            yield StreamChunk(
                content=f"AI服务暂时不可用: {str(e)}",
                is_final=True,
                finish_reason="error"
            )
    
    async def _build_request_messages(
        self,
        messages: List[Dict[str, str]],
        ai_role: Optional[AIRole] = None
    ) -> List[Dict[str, str]]:
        """
        构建请求消息列表
        
        Args:
            messages: 原始消息列表
            ai_role: AI角色信息
            
        Returns:
            List[Dict[str, str]]: 格式化的请求消息
        """
        request_messages = []
        
        # 添加系统提示（如果有AI角色）
        if ai_role and ai_role.system_prompt:
            request_messages.append({
                "role": "system",
                "content": ai_role.system_prompt
            })
        
        # 添加对话消息
        for message in messages:
            if message.get("role") in ["user", "assistant", "system"]:
                request_messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
        
        return request_messages
    
    async def _generate_single_response(
        self,
        request_data: Dict[str, Any],
        start_time: float
    ) -> AIResponse:
        """
        生成单次AI响应
        
        Args:
            request_data: 请求数据
            start_time: 开始时间
            
        Returns:
            AIResponse: AI响应结果
        """
        response = await self.http_client.post(
            self.qwen_api_url,
            json=request_data
        )
        
        if response.status_code != 200:
            error_text = response.text
            raise Exception(f"API请求失败: {response.status_code} - {error_text}")
        
        result = response.json()
        
        # 解析响应
        if "output" not in result:
            raise Exception("API响应格式错误")
        
        output = result["output"]
        content = output.get("text", "")
        finish_reason = output.get("finish_reason", "stop")
        
        # 获取token使用量
        tokens_used = 0
        if "usage" in result:
            usage = result["usage"]
            tokens_used = usage.get("total_tokens", 0)
        
        response_time = time.time() - start_time
        
        return AIResponse(
            content=content,
            model=self.qwen_model,
            tokens_used=tokens_used,
            finish_reason=finish_reason,
            response_time=response_time
        )
    
    async def _generate_stream_response(
        self,
        request_data: Dict[str, Any],
        start_time: float
    ) -> AIResponse:
        """
        生成流式响应（用于非流式接口）
        
        Args:
            request_data: 请求数据
            start_time: 开始时间
            
        Returns:
            AIResponse: AI响应结果
        """
        full_content = ""
        tokens_used = 0
        finish_reason = "stop"
        
        async for chunk in self.generate_stream_response([]):
            if chunk.is_final:
                if chunk.tokens_used:
                    tokens_used = chunk.tokens_used
                if chunk.finish_reason:
                    finish_reason = chunk.finish_reason
                break
            else:
                full_content += chunk.content
        
        response_time = time.time() - start_time
        
        return AIResponse(
            content=full_content,
            model=self.qwen_model,
            tokens_used=tokens_used,
            finish_reason=finish_reason,
            response_time=response_time
        )
    
    async def close(self):
        """
        关闭HTTP客户端
        """
        await self.http_client.aclose()


# 全局AI客户端实例
_ai_client: Optional[AIClient] = None


async def get_ai_client() -> AIClient:
    """
    获取AI客户端实例
    
    Returns:
        AIClient: AI客户端实例
    """
    global _ai_client
    
    if _ai_client is None:
        from ..core.database import get_database_manager
        db = await get_database_manager()
        _ai_client = AIClient(db)
    
    return _ai_client


async def close_ai_client():
    """
    关闭AI客户端
    """
    global _ai_client
    
    if _ai_client:
        await _ai_client.close()
        _ai_client = None