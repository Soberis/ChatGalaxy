#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 日志配置模块

配置应用的日志系统:
- 日志格式化
- 日志轮转
- 多级别日志
- 文件和控制台输出
"""

import sys
import logging
from pathlib import Path
from loguru import logger
from typing import Dict, Any

from .config import settings


class InterceptHandler(logging.Handler):
    """
    拦截标准库日志并重定向到loguru
    
    将Python标准库的logging模块日志重定向到loguru处理
    确保所有日志都使用统一的格式和配置
    """
    
    def emit(self, record: logging.LogRecord):
        """
        处理日志记录
        
        Args:
            record: 日志记录对象
        """
        # 获取对应的loguru日志级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        # 查找调用者信息
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        # 使用loguru记录日志
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """
    设置应用日志配置
    
    配置loguru日志系统，包括:
    - 控制台输出格式
    - 文件输出和轮转
    - 日志级别过滤
    - 标准库日志拦截
    """
    # 移除默认的loguru处理器
    logger.remove()
    
    # 创建日志目录
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 控制台日志配置
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # 文件日志配置
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=console_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # 添加文件处理器
    logger.add(
        settings.LOG_FILE,
        format=file_format,
        level=settings.LOG_LEVEL,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        backtrace=True,
        diagnose=True,
        encoding="utf-8"
    )
    
    # 添加错误日志文件处理器
    error_log_file = str(Path(settings.LOG_FILE).with_suffix('.error.log'))
    logger.add(
        error_log_file,
        format=file_format,
        level="ERROR",
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        backtrace=True,
        diagnose=True,
        encoding="utf-8"
    )
    
    # 拦截标准库日志
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # 设置第三方库日志级别
    for logger_name in [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "supabase",
        "httpx",
        "websockets"
    ]:
        logging.getLogger(logger_name).handlers = [InterceptHandler()]
        logging.getLogger(logger_name).propagate = False
    
    # 记录日志系统启动信息
    logger.info("📝 日志系统初始化完成")
    logger.info(f"📁 日志文件: {settings.LOG_FILE}")
    logger.info(f"📊 日志级别: {settings.LOG_LEVEL}")
    logger.info(f"🔄 日志轮转: {settings.LOG_ROTATION}")
    logger.info(f"🗂️ 日志保留: {settings.LOG_RETENTION}")


def get_logger(name: str) -> Any:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        Any: loguru日志记录器
    """
    return logger.bind(name=name)


def log_request(request_id: str, method: str, url: str, **kwargs) -> None:
    """
    记录HTTP请求日志
    
    Args:
        request_id: 请求ID
        method: HTTP方法
        url: 请求URL
        **kwargs: 额外的日志信息
    """
    extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(
        f"🌐 HTTP请求 | ID={request_id} | {method} {url}"
        + (f" | {extra_info}" if extra_info else "")
    )


def log_response(request_id: str, status_code: int, duration: float, **kwargs) -> None:
    """
    记录HTTP响应日志
    
    Args:
        request_id: 请求ID
        status_code: HTTP状态码
        duration: 请求处理时间(秒)
        **kwargs: 额外的日志信息
    """
    extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    
    # 根据状态码选择日志级别
    if status_code >= 500:
        log_func = logger.error
        emoji = "❌"
    elif status_code >= 400:
        log_func = logger.warning
        emoji = "⚠️"
    else:
        log_func = logger.info
        emoji = "✅"
    
    log_func(
        f"{emoji} HTTP响应 | ID={request_id} | {status_code} | {duration:.3f}s"
        + (f" | {extra_info}" if extra_info else "")
    )


def log_websocket_event(event_type: str, connection_id: str, **kwargs) -> None:
    """
    记录WebSocket事件日志
    
    Args:
        event_type: 事件类型 (connect, disconnect, message, error)
        connection_id: 连接ID
        **kwargs: 额外的日志信息
    """
    extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    
    emoji_map = {
        "connect": "🔌",
        "disconnect": "🔌",
        "message": "💬",
        "error": "❌"
    }
    
    emoji = emoji_map.get(event_type, "📡")
    
    logger.info(
        f"{emoji} WebSocket事件 | {event_type.upper()} | ID={connection_id}"
        + (f" | {extra_info}" if extra_info else "")
    )


def log_ai_request(model: str, prompt_length: int, **kwargs) -> None:
    """
    记录AI服务请求日志
    
    Args:
        model: AI模型名称
        prompt_length: 提示词长度
        **kwargs: 额外的日志信息
    """
    extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    
    logger.info(
        f"🤖 AI请求 | 模型={model} | 提示词长度={prompt_length}"
        + (f" | {extra_info}" if extra_info else "")
    )


def log_ai_response(model: str, response_length: int, duration: float, **kwargs) -> None:
    """
    记录AI服务响应日志
    
    Args:
        model: AI模型名称
        response_length: 响应长度
        duration: 处理时间(秒)
        **kwargs: 额外的日志信息
    """
    extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    
    logger.info(
        f"🤖 AI响应 | 模型={model} | 响应长度={response_length} | {duration:.3f}s"
        + (f" | {extra_info}" if extra_info else "")
    )


if __name__ == "__main__":
    """
    测试日志配置
    """
    # 设置日志
    setup_logging()
    
    # 测试各种日志级别
    logger.debug("🐛 这是调试信息")
    logger.info("ℹ️ 这是普通信息")
    logger.warning("⚠️ 这是警告信息")
    logger.error("❌ 这是错误信息")
    
    # 测试专用日志函数
    log_request("req-123", "GET", "/api/test", user_id="user-456")
    log_response("req-123", 200, 0.123, size="1.2KB")
    log_websocket_event("connect", "ws-789", user_id="user-456")
    log_ai_request("qwen-turbo", 150, user_id="user-456")
    log_ai_response("qwen-turbo", 300, 1.234, tokens=50)
    
    logger.success("✅ 日志测试完成")