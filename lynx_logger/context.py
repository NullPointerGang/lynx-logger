"""
Контекстное логирование и процессоры контекста
"""

import os
import threading
import uuid
from contextvars import ContextVar
from typing import Dict, Any, Optional
import structlog


request_id_ctx: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_ctx: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
trace_id_ctx: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)


class RequestContext:
    """Контекст запроса для трассировки"""
    
    def __init__(self, request_id: str | None = None, user_id: str | None = None, trace_id: str | None = None, session_id: str | None = None):
        """
        Args:
            request_id: Идентификатор запроса
            user_id: Идентификатор пользователя
            trace_id: Идентификатор трассировки
            session_id: Идентификатор сессии
        """
        self.request_id = request_id or str(uuid.uuid4())
        self.user_id = user_id
        self.trace_id = trace_id or str(uuid.uuid4())
        self.session_id = session_id
        
        self._prev_request_id = None
        self._prev_user_id = None
        self._prev_trace_id = None
        self._prev_session_id = None
    
    def __enter__(self):
        """Вход в контекст"""
        self._prev_request_id = request_id_ctx.set(self.request_id)
        self._prev_user_id = user_id_ctx.set(self.user_id)
        self._prev_trace_id = trace_id_ctx.set(self.trace_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекста"""
        if self._prev_request_id:
            request_id_ctx.reset(self._prev_request_id)
        if self._prev_user_id:
            user_id_ctx.reset(self._prev_user_id)
        if self._prev_trace_id:
            trace_id_ctx.reset(self._prev_trace_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        result = {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "trace_id": self.trace_id
        }
        if self.session_id:
            result["session_id"] = self.session_id
        return result


class ContextProcessor:
    """Процессоры для добавления контекстной информации"""
    
    @staticmethod
    def add_request_context(logger, name, event_dict):
        """Добавляет контекст запроса в лог"""
        request_id = request_id_ctx.get()
        user_id = user_id_ctx.get()
        trace_id = trace_id_ctx.get()
        
        if request_id:
            event_dict["request_id"] = request_id
        if user_id:
            event_dict["user_id"] = user_id
        if trace_id:
            event_dict["trace_id"] = trace_id
        
        return event_dict
    
    @staticmethod
    def add_thread_info(logger, name, event_dict):
        """Добавляет информацию о потоке"""
        event_dict["thread_id"] = threading.get_ident()
        event_dict["thread_name"] = threading.current_thread().name
        return event_dict
    
    @staticmethod
    def add_process_info(logger, name, event_dict):
        """Добавляет информацию о процессе"""
        event_dict["process_id"] = os.getpid()
        return event_dict
    
    @staticmethod
    def add_hostname(logger, name, event_dict):
        """Добавляет имя хоста"""
        import socket
        event_dict["hostname"] = socket.gethostname()
        return event_dict
    
    @staticmethod
    def add_hostname_info(logger, name, event_dict):
        """Алиас для add_hostname для совместимости с тестами"""
        return ContextProcessor.add_hostname(logger, name, event_dict)
    
    @staticmethod
    def add_caller_info(logger, name, event_dict):
        """Добавляет информацию о вызывающем коде"""
        import inspect
        frame = inspect.currentframe().f_back
        if frame:
            event_dict["caller_module"] = frame.f_globals.get('__name__', 'unknown')
            event_dict["caller_function"] = frame.f_code.co_name
            event_dict["caller_line"] = frame.f_lineno
        return event_dict
    
    @staticmethod
    def add_custom_fields(custom_fields: Dict[str, Any]):
        """Создает процессор для добавления пользовательских полей"""
        def processor(logger, name, event_dict):
            event_dict.update(custom_fields)
            return event_dict
        return processor


class ContextLogger:
    """Логгер с автоматическим управлением контекстом"""
    
    def __init__(self, base_logger: structlog.BoundLogger):
        """
        Args:
            base_logger: Базовый structlog логгер
        """
        self.base_logger = base_logger
        self._context_stack = []
    
    @property
    def _logger(self):
        """Свойство для совместимости с тестами"""
        return self.base_logger
    
    def push_context(self, context_dict: dict = None, **kwargs) -> "ContextLogger":
        """
        Добавляет контекст в стек
        
        Args:
            context_dict: Словарь контекста (может быть передан как позиционный аргумент)
            **kwargs: Поля контекста
            
        Returns:
            Новый ContextLogger с добавленным контекстом
        """
        if context_dict:
            self._context_stack.append(context_dict)
            bound_logger = self.base_logger.bind(**context_dict)
        else:
            self._context_stack.append(kwargs)
            bound_logger = self.base_logger.bind(**kwargs)
        
        new_logger = ContextLogger(bound_logger)
        new_logger._context_stack = self._context_stack.copy()
        return new_logger
    
    def pop_context(self) -> "ContextLogger":
        """
        Удаляет последний контекст из стека
        
        Returns:
            Новый ContextLogger без последнего контекста
        """
        if not self._context_stack:
            return self
        
        self._context_stack.pop()
        
        bound_logger = self.base_logger
        for context in self._context_stack:
            bound_logger = bound_logger.bind(**context)
        
        new_logger = ContextLogger(bound_logger)
        new_logger._context_stack = self._context_stack.copy()
        return new_logger
    
    def with_request(self, request_id: str | None = None, user_id: str | None = None) -> "ContextLogger":
        """
        Добавляет контекст запроса
        
        Args:
            request_id: ID запроса
            user_id: ID пользователя
            
        Returns:
            ContextLogger с контекстом запроса
        """
        context = {}
        if request_id:
            context["request_id"] = request_id
        if user_id:
            context["user_id"] = user_id
        
        return self.push_context(**context)
    
    def with_trace(self, trace_id: str) -> "ContextLogger":
        """
        Добавляет трассировочный ID
        
        Args:
            trace_id: ID трассировки
            
        Returns:
            ContextLogger с трассировочным ID
        """
        return self.push_context(trace_id=trace_id)
    
    def with_operation(self, operation: str) -> "ContextLogger":
        """
        Добавляет операцию в контекст
        
        Args:
            operation: Название операции
            
        Returns:
            ContextLogger с операцией
        """
        return self.push_context(operation=operation)
    
    def with_user(self, user_id: str) -> "ContextLogger":
        """
        Добавляет пользователя в контекст
        
        Args:
            user_id: ID пользователя
            
        Returns:
            ContextLogger с пользователем
        """
        return self.push_context(user_id=user_id)
    
    def with_context(self, context_dict: dict = None, **kwargs) -> "ContextLogger":
        """
        Добавляет контекст из словаря или kwargs
        
        Args:
            context_dict: Словарь контекста
            **kwargs: Поля контекста
            
        Returns:
            ContextLogger с контекстом
        """
        if context_dict:
            return self.push_context(**context_dict)
        return self.push_context(**kwargs)
    
    def clear_context(self) -> "ContextLogger":
        """
        Очищает весь контекст
        
        Returns:
            ContextLogger без контекста
        """
        return ContextLogger(self.base_logger)
    
    def get_current_context(self) -> dict:
        """
        Получает текущий контекст
        
        Returns:
            Словарь текущего контекста
        """
        current_context = {}
        for context in self._context_stack:
            current_context.update(context)
        return current_context
    
    def bind(self, **kwargs) -> "ContextLogger":
        """
        Привязывает дополнительные поля
        
        Args:
            **kwargs: Поля для привязки
            
        Returns:
            ContextLogger с привязанными полями
        """
        return self.push_context(**kwargs)
    
    # Методы логирования
    def debug(self, message: str, **kwargs):
        """Логирование DEBUG"""
        return self.base_logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Логирование INFO"""
        return self.base_logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Логирование WARNING"""
        return self.base_logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Логирование ERROR"""
        return self.base_logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Логирование CRITICAL"""
        return self.base_logger.critical(message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Логирование исключения"""
        return self.base_logger.exception(message, **kwargs)


class CorrelationIDProcessor:
    """Процессор для автоматического добавления correlation ID"""
    
    def __init__(self, header_name: str = "X-Correlation-ID"):
        """
        Args:
            header_name: Имя заголовка для correlation ID
        """
        self.header_name = header_name
        self._correlation_id = None
    
    def set_correlation_id(self, correlation_id: str):
        """Устанавливает correlation ID"""
        self._correlation_id = correlation_id
    
    def get_correlation_id(self) -> Optional[str]:
        """Получает текущий correlation ID"""
        return self._correlation_id
    
    def clear_correlation_id(self):
        """Очищает correlation ID"""
        self._correlation_id = None
    
    def processor(self, logger, name, event_dict):
        """Процессор для добавления correlation ID в логи"""
        if self._correlation_id:
            event_dict["correlation_id"] = self._correlation_id
        return event_dict 
    
