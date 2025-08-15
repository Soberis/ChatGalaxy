#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy API响应工具模块

提供统一的API响应格式和处理函数:
- 成功响应格式化
- 错误响应格式化
- 分页响应处理
- 状态码管理
"""

from typing import Any, Optional, Dict, List
from datetime import datetime
from fastapi import status
from pydantic import BaseModel


class APIResponse(BaseModel):
    """
    API响应基础模型
    """
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginationInfo(BaseModel):
    """
    分页信息模型
    """
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(APIResponse):
    """
    分页响应模型
    """
    pagination: PaginationInfo


def success_response(
    data: Any = None,
    message: str = "操作成功",
    status_code: int = status.HTTP_200_OK
) -> Dict[str, Any]:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        status_code: HTTP状态码
        
    Returns:
        Dict[str, Any]: 格式化的成功响应
    """
    response = APIResponse(
        success=True,
        message=message,
        data=data,
        timestamp=datetime.utcnow()
    )
    
    return response.dict()


def error_response(
    message: str = "操作失败",
    data: Any = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> Dict[str, Any]:
    """
    创建错误响应
    
    Args:
        message: 错误消息
        data: 错误详情数据
        status_code: HTTP状态码
        
    Returns:
        Dict[str, Any]: 格式化的错误响应
    """
    response = APIResponse(
        success=False,
        message=message,
        data=data,
        timestamp=datetime.utcnow()
    )
    
    return response.dict()


def paginated_response(
    data: List[Any],
    page: int,
    page_size: int,
    total: int,
    message: str = "获取数据成功"
) -> Dict[str, Any]:
    """
    创建分页响应
    
    Args:
        data: 分页数据列表
        page: 当前页码
        page_size: 每页大小
        total: 总记录数
        message: 响应消息
        
    Returns:
        Dict[str, Any]: 格式化的分页响应
    """
    total_pages = (total + page_size - 1) // page_size
    
    pagination = PaginationInfo(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )
    
    response = PaginatedResponse(
        success=True,
        message=message,
        data=data,
        pagination=pagination,
        timestamp=datetime.utcnow()
    )
    
    return response.dict()


def validation_error_response(
    errors: List[Dict[str, Any]],
    message: str = "数据验证失败"
) -> Dict[str, Any]:
    """
    创建数据验证错误响应
    
    Args:
        errors: 验证错误列表
        message: 错误消息
        
    Returns:
        Dict[str, Any]: 格式化的验证错误响应
    """
    return error_response(
        message=message,
        data={"validation_errors": errors},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


def unauthorized_response(
    message: str = "未授权访问"
) -> Dict[str, Any]:
    """
    创建未授权响应
    
    Args:
        message: 错误消息
        
    Returns:
        Dict[str, Any]: 格式化的未授权响应
    """
    return error_response(
        message=message,
        status_code=status.HTTP_401_UNAUTHORIZED
    )


def forbidden_response(
    message: str = "禁止访问"
) -> Dict[str, Any]:
    """
    创建禁止访问响应
    
    Args:
        message: 错误消息
        
    Returns:
        Dict[str, Any]: 格式化的禁止访问响应
    """
    return error_response(
        message=message,
        status_code=status.HTTP_403_FORBIDDEN
    )


def not_found_response(
    message: str = "资源不存在"
) -> Dict[str, Any]:
    """
    创建资源不存在响应
    
    Args:
        message: 错误消息
        
    Returns:
        Dict[str, Any]: 格式化的资源不存在响应
    """
    return error_response(
        message=message,
        status_code=status.HTTP_404_NOT_FOUND
    )


def server_error_response(
    message: str = "服务器内部错误"
) -> Dict[str, Any]:
    """
    创建服务器错误响应
    
    Args:
        message: 错误消息
        
    Returns:
        Dict[str, Any]: 格式化的服务器错误响应
    """
    return error_response(
        message=message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )