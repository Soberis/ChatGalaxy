#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGalaxy 日志工具模块

提供统一的日志记录功能:
- 日志配置管理
- 格式化日志输出
- 文件日志轮转
- 不同级别日志处理
"""

import logging
import logging.handlers
import os
import sys
from typing import Optional
from datetime import datetime

from ..config import get_settings


class ColoredFormatter(logging.Formatter):
    """
    彩色日志格式化器
    """
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def format(self, record):
        """
        格式化日志记录
        
        Args:
            record: 日志记录对象
            
        Returns:
            str: 格式化后的日志字符串
        """
        # 获取原始格式化结果
        log_message = super().format(record)
        
        # 添加颜色
        if record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            reset = self.COLORS['RESET']
            log_message = f"{color}{log_message}{reset}"
        
        return log_message


class ChatGalaxyLogger:
    """
    ChatGalaxy日志管理器
    """
    
    def __init__(self):
        self.settings = get_settings()
        self._loggers = {}
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """
        设置根日志记录器
        """
        # 获取根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.settings.LOG_LEVEL.upper()))
        
        # 清除现有处理器
        root_logger.handlers.clear()
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # 控制台格式化器（带颜色）
        console_formatter = ColoredFormatter(
            fmt=self.settings.LOG_FORMAT,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # 文件处理器（如果配置了日志文件）
        if self.settings.LOG_FILE:
            self._setup_file_handler(root_logger)
    
    def _setup_file_handler(self, logger: logging.Logger):
        """
        设置文件日志处理器
        
        Args:
            logger: 日志记录器
        """
        # 确保日志目录存在
        log_dir = os.path.dirname(self.settings.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 创建轮转文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            filename=self.settings.LOG_FILE,
            maxBytes=self.settings.LOG_MAX_SIZE,
            backupCount=self.settings.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 文件格式化器（不带颜色）
        file_formatter = logging.Formatter(
            fmt=self.settings.LOG_FORMAT,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        获取指定名称的日志记录器
        
        Args:
            name: 日志记录器名称
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        if name not in self._loggers:
            logger = logging.getLogger(name)
            self._loggers[name] = logger
        
        return self._loggers[name]
    
    def log_request(self, method: str, path: str, status_code: int, 
                   duration: float, user_id: Optional[str] = None):
        """
        记录HTTP请求日志
        
        Args:
            method: HTTP方法
            path: 请求路径
            status_code: 状态码
            duration: 请求耗时（秒）
            user_id: 用户ID（可选）
        """
        logger = self.get_logger("chatgalaxy.request")
        
        user_info = f" [User: {user_id}]" if user_id else ""
        logger.info(
            f"{method} {path} - {status_code} - {duration:.3f}s{user_info}"
        )
    
    def log_error(self, error: Exception, context: Optional[dict] = None):
        """
        记录错误日志
        
        Args:
            error: 异常对象
            context: 错误上下文信息
        """
        logger = self.get_logger("chatgalaxy.error")
        
        error_msg = f"Error: {str(error)}"
        if context:
            error_msg += f" | Context: {context}"
        
        logger.error(error_msg, exc_info=True)
    
    def log_auth_event(self, event_type: str, user_email: str, 
                      success: bool, details: Optional[str] = None):
        """
        记录认证事件日志
        
        Args:
            event_type: 事件类型（login, register, logout等）
            user_email: 用户邮箱
            success: 是否成功
            details: 详细信息
        """
        logger = self.get_logger("chatgalaxy.auth")
        
        status = "SUCCESS" if success else "FAILED"
        msg = f"Auth {event_type.upper()} - {user_email} - {status}"
        
        if details:
            msg += f" | {details}"
        
        if success:
            logger.info(msg)
        else:
            logger.warning(msg)
    
    def log_ai_request(self, model: str, tokens_used: int, 
                      duration: float, user_id: Optional[str] = None):
        """
        记录AI请求日志
        
        Args:
            model: AI模型名称
            tokens_used: 使用的token数量
            duration: 请求耗时（秒）
            user_id: 用户ID（可选）
        """
        logger = self.get_logger("chatgalaxy.ai")
        
        user_info = f" [User: {user_id}]" if user_id else ""
        logger.info(
            f"AI Request - Model: {model}, Tokens: {tokens_used}, "
            f"Duration: {duration:.3f}s{user_info}"
        )


# 全局日志管理器实例
_logger_manager = None


def get_logger_manager() -> ChatGalaxyLogger:
    """
    获取全局日志管理器实例
    
    Returns:
        ChatGalaxyLogger: 日志管理器实例
    """
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = ChatGalaxyLogger()
    return _logger_manager


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    return get_logger_manager().get_logger(name)


def log_request(method: str, path: str, status_code: int, 
               duration: float, user_id: Optional[str] = None):
    """
    记录HTTP请求日志
    
    Args:
        method: HTTP方法
        path: 请求路径
        status_code: 状态码
        duration: 请求耗时（秒）
        user_id: 用户ID（可选）
    """
    get_logger_manager().log_request(method, path, status_code, duration, user_id)


def log_error(error: Exception, context: Optional[dict] = None):
    """
    记录错误日志
    
    Args:
        error: 异常对象
        context: 错误上下文信息
    """
    get_logger_manager().log_error(error, context)


def log_auth_event(event_type: str, user_email: str, 
                  success: bool, details: Optional[str] = None):
    """
    记录认证事件日志
    
    Args:
        event_type: 事件类型（login, register, logout等）
        user_email: 用户邮箱
        success: 是否成功
        details: 详细信息
    """
    get_logger_manager().log_auth_event(event_type, user_email, success, details)


def log_ai_request(model: str, tokens_used: int, 
                  duration: float, user_id: Optional[str] = None):
    """
    记录AI请求日志
    
    Args:
        model: AI模型名称
        tokens_used: 使用的token数量
        duration: 请求耗时（秒）
        user_id: 用户ID（可选）
    """
    get_logger_manager().log_ai_request(model, tokens_used, duration, user_id)