#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy AI客户端模块

集成阿里通义千问API:
- AI对话生成
- 流式响应支持
- 多角色对话
- 上下文管理
- 错误处理和重试
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, AsyncGenerator, Any
from datetime import datetime
from enum import Enum
import aiohttp
from pydantic import BaseModel

from ..config import get_settings
from ..models.ai_role import AIRole



class AIProvider(Enum):
    """AI服务提供商枚举"""
    QWEN = "qwen"  # 阿里通义千问
    OPENAI = "openai"  # OpenAI GPT
    CLAUDE = "claude"  # Anthropic Claude


class AIMessage(BaseModel):
    """AI消息模型"""
    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None


class AIResponse(BaseModel):
    """AI响应模型"""
    content: str
    tokens_used: int
    model: str
    finish_reason: str
    response_time: float
    metadata: Optional[Dict[str, Any]] = None


class StreamChunk(BaseModel):
    """流式响应块模型"""
    content: str
    is_complete: bool
    tokens_used: int
    finish_reason: Optional[str] = None


class AIClient:
    """
    AI客户端类
    
    提供与AI服务的统一接口
    """
    
    def __init__(self, provider: AIProvider = AIProvider.QWEN):
        """
        初始化AI客户端
        
        Args:
            provider: AI服务提供商
        """
        self.provider = provider
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # 配置API参数
        self._setup_provider_config()
        
        # HTTP会话
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 重试配置
        self.max_retries = 3
        self.retry_delay = 1.0
    
    def _setup_provider_config(self):
        """
        设置AI服务提供商配置
        """
        if self.provider == AIProvider.QWEN:
            self.api_key = self.settings.QWEN_API_KEY
            self.api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            self.model_name = "qwen-turbo"  # 默认模型
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-DashScope-SSE": "enable"  # 启用流式响应
            }
        elif self.provider == AIProvider.OPENAI:
            self.api_key = self.settings.OPENAI_API_KEY
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.model_name = "gpt-3.5-turbo"
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        else:
            raise ValueError(f"不支持的AI服务提供商: {self.provider}")
    
    async def __aenter__(self):
        """
        异步上下文管理器入口
        """
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        异步上下文管理器出口
        """
        if self.session:
            await self.session.close()
    
    def _build_messages(
        self, 
        content: str, 
        ai_role: AIRole,
        context_messages: Optional[List[Dict[str, str]]] = None
    ) -> List[AIMessage]:
        """
        构建AI对话消息列表
        
        Args:
            content: 用户消息内容
            ai_role: AI角色信息
            context_messages: 上下文消息
            
        Returns:
            List[AIMessage]: 消息列表
        """
        messages = []
        
        # 系统提示词
        if ai_role.system_prompt:
            messages.append(AIMessage(
                role="system",
                content=ai_role.system_prompt
            ))
        
        # 上下文消息
        if context_messages:
            for msg in context_messages[-10:]:  # 限制上下文长度
                messages.append(AIMessage(
                    role=msg.get("role", "user"),
                    content=msg.get("content", "")
                ))
        
        # 当前用户消息
        messages.append(AIMessage(
            role="user",
            content=content
        ))
        
        return messages
    
    def _build_qwen_payload(
        self, 
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        构建通义千问API请求载荷
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式响应
            
        Returns:
            Dict[str, Any]: 请求载荷
        """
        return {
            "model": self.model_name,
            "input": {
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content
                    } for msg in messages
                ]
            },
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": 0.8,
                "repetition_penalty": 1.1,
                "incremental_output": stream
            }
        }
    
    def _build_openai_payload(
        self, 
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        构建OpenAI API请求载荷
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式响应
            
        Returns:
            Dict[str, Any]: 请求载荷
        """
        return {
            "model": self.model_name,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content
                } for msg in messages
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
    
    async def generate_response(
        self,
        content: str,
        ai_role: AIRole,
        context_messages: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AIResponse:
        """
        生成AI响应
        
        Args:
            content: 用户消息内容
            ai_role: AI角色信息
            context_messages: 上下文消息
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            AIResponse: AI响应
        """
        start_time = datetime.utcnow()
        
        try:
            # 构建消息
            messages = self._build_messages(content, ai_role, context_messages)
            
            # 构建请求载荷
            if self.provider == AIProvider.QWEN:
                payload = self._build_qwen_payload(
                    messages, temperature, max_tokens, stream=False
                )
            elif self.provider == AIProvider.OPENAI:
                payload = self._build_openai_payload(
                    messages, temperature, max_tokens, stream=False
                )
            else:
                raise ValueError(f"不支持的AI服务提供商: {self.provider}")
            
            # 发送请求
            response_data = await self._make_request(payload)
            
            # 解析响应
            ai_response = self._parse_response(response_data, start_time)
            
            self.logger.info(f"AI响应生成成功: {ai_response.tokens_used} tokens")
            return ai_response
            
        except Exception as e:
            self.logger.error(f"AI响应生成失败: {str(e)}")
            raise
    
    async def generate_stream_response(
        self,
        content: str,
        ai_role: AIRole,
        context_messages: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        生成流式AI响应
        
        Args:
            content: 用户消息内容
            ai_role: AI角色信息
            context_messages: 上下文消息
            temperature: 温度参数
            max_tokens: 最大token数
            
        Yields:
            StreamChunk: 流式响应块
        """
        try:
            # 构建消息
            messages = self._build_messages(content, ai_role, context_messages)
            
            # 构建请求载荷
            if self.provider == AIProvider.QWEN:
                payload = self._build_qwen_payload(
                    messages, temperature, max_tokens, stream=True
                )
            elif self.provider == AIProvider.OPENAI:
                payload = self._build_openai_payload(
                    messages, temperature, max_tokens, stream=True
                )
            else:
                raise ValueError(f"不支持的AI服务提供商: {self.provider}")
            
            # 发送流式请求
            async for chunk in self._make_stream_request(payload):
                yield chunk
                
        except Exception as e:
            self.logger.error(f"流式AI响应生成失败: {str(e)}")
            # 发送错误块
            yield StreamChunk(
                content=f"错误: {str(e)}",
                is_complete=True,
                tokens_used=0,
                finish_reason="error"
            )
    
    async def _make_request(
        self, 
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            payload: 请求载荷
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        if not self.session:
            raise RuntimeError("HTTP会话未初始化")
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=error_text
                        )
                        
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                
                self.logger.warning(
                    f"请求失败，第 {attempt + 1} 次重试: {str(e)}"
                )
                await asyncio.sleep(self.retry_delay * (attempt + 1))
    
    async def _make_stream_request(
        self, 
        payload: Dict[str, Any]
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        发送流式HTTP请求
        
        Args:
            payload: 请求载荷
            
        Yields:
            StreamChunk: 流式响应块
        """
        if not self.session:
            raise RuntimeError("HTTP会话未初始化")
        
        try:
            async with self.session.post(
                self.api_url,
                headers=self.headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=error_text
                    )
                
                # 处理流式响应
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if not line or not line.startswith('data:'):
                        continue
                    
                    # 解析SSE数据
                    data_str = line[5:].strip()  # 移除 'data:' 前缀
                    
                    if data_str == '[DONE]':
                        yield StreamChunk(
                            content="",
                            is_complete=True,
                            tokens_used=0,
                            finish_reason="stop"
                        )
                        break
                    
                    try:
                        data = json.loads(data_str)
                        chunk = self._parse_stream_chunk(data)
                        if chunk:
                            yield chunk
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            self.logger.error(f"流式请求失败: {str(e)}")
            raise
    
    def _parse_response(
        self, 
        response_data: Dict[str, Any], 
        start_time: datetime
    ) -> AIResponse:
        """
        解析AI响应数据
        
        Args:
            response_data: 响应数据
            start_time: 请求开始时间
            
        Returns:
            AIResponse: 解析后的响应
        """
        try:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            if self.provider == AIProvider.QWEN:
                output = response_data.get("output", {})
                usage = response_data.get("usage", {})
                
                return AIResponse(
                    content=output.get("text", ""),
                    tokens_used=usage.get("total_tokens", 0),
                    model=self.model_name,
                    finish_reason=output.get("finish_reason", "stop"),
                    response_time=response_time,
                    metadata={
                        "input_tokens": usage.get("input_tokens", 0),
                        "output_tokens": usage.get("output_tokens", 0)
                    }
                )
            
            elif self.provider == AIProvider.OPENAI:
                choice = response_data.get("choices", [{}])[0]
                usage = response_data.get("usage", {})
                
                return AIResponse(
                    content=choice.get("message", {}).get("content", ""),
                    tokens_used=usage.get("total_tokens", 0),
                    model=response_data.get("model", self.model_name),
                    finish_reason=choice.get("finish_reason", "stop"),
                    response_time=response_time,
                    metadata={
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0)
                    }
                )
            
            else:
                raise ValueError(f"不支持的AI服务提供商: {self.provider}")
                
        except Exception as e:
            self.logger.error(f"解析AI响应失败: {str(e)}")
            raise
    
    def _parse_stream_chunk(
        self, 
        chunk_data: Dict[str, Any]
    ) -> Optional[StreamChunk]:
        """
        解析流式响应块
        
        Args:
            chunk_data: 响应块数据
            
        Returns:
            Optional[StreamChunk]: 解析后的响应块
        """
        try:
            if self.provider == AIProvider.QWEN:
                output = chunk_data.get("output", {})
                usage = chunk_data.get("usage", {})
                
                return StreamChunk(
                    content=output.get("text", ""),
                    is_complete=output.get("finish_reason") is not None,
                    tokens_used=usage.get("total_tokens", 0),
                    finish_reason=output.get("finish_reason")
                )
            
            elif self.provider == AIProvider.OPENAI:
                choice = chunk_data.get("choices", [{}])[0]
                delta = choice.get("delta", {})
                
                return StreamChunk(
                    content=delta.get("content", ""),
                    is_complete=choice.get("finish_reason") is not None,
                    tokens_used=0,  # OpenAI流式响应不包含token统计
                    finish_reason=choice.get("finish_reason")
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"解析流式响应块失败: {str(e)}")
            return None


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
        _ai_client = AIClient()
    
    return _ai_client


async def close_ai_client():
    """
    关闭AI客户端
    """
    global _ai_client
    
    if _ai_client and _ai_client.session:
        await _ai_client.session.close()
        _ai_client = None