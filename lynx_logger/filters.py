"""
Фильтры для логирования
"""

import logging
import re
from typing import List, Callable
from .config import Level


class LogFilter:
    """Базовый класс для фильтров логов"""
    
    @staticmethod
    def level_filter(min_level: Level) -> Callable:
        """
        Фильтр по минимальному уровню логирования
        
        Args:
            min_level: Минимальный уровень для пропуска сообщений
        
        Returns:
            Функция фильтра
        """
        def filter_func(record: logging.LogRecord) -> bool:
            return record.levelno >= min_level.value
        
        return filter_func
    
    @staticmethod
    def exclude_loggers(logger_names: List[str]) -> Callable:
        """
        Исключает сообщения от определенных логгеров
        
        Args:
            logger_names: Список имен логгеров для исключения
        
        Returns:
            Функция фильтра
        """
        def filter_func(record: logging.LogRecord) -> bool:
            return record.name not in logger_names
        
        return filter_func
    
    @staticmethod
    def include_only(logger_names: List[str]) -> Callable:
        """
        Включает только сообщения от определенных логгеров
        
        Args:
            logger_names: Список имен логгеров для включения
        
        Returns:
            Функция фильтра
        """
        def filter_func(record: logging.LogRecord) -> bool:
            return record.name in logger_names
        
        return filter_func
    
    @staticmethod
    def exclude_messages(patterns: List[str]) -> Callable:
        """
        Исключает сообщения по регулярным выражениям
        
        Args:
            patterns: Список regex паттернов для исключения
        
        Returns:
            Функция фильтра
        """
        compiled_patterns = [re.compile(pattern) for pattern in patterns]
        
        def filter_func(record: logging.LogRecord) -> bool:
            message = record.getMessage()
            return not any(pattern.search(message) for pattern in compiled_patterns)
        
        return filter_func
    
    @staticmethod
    def custom_filter(condition: Callable[[logging.LogRecord], bool]) -> Callable:
        """
        Создает пользовательский фильтр
        
        Args:
            condition: Функция, которая принимает LogRecord и возвращает bool
        
        Returns:
            Функция фильтра
        """
        return condition


class LevelFilter(logging.Filter):
    """Фильтр для фильтрации по уровню логирования"""
    
    def __init__(self, min_level: Level, max_level: Level | None = None):
        """
        Args:
            min_level: Минимальный уровень
            max_level: Максимальный уровень (опционально)
        """
        super().__init__()
        self.min_level = min_level.value
        self.max_level = max_level.value if max_level else float('inf')
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Фильтрация записи"""
        return self.min_level <= record.levelno <= self.max_level


class SourceFilter(logging.Filter):
    """Фильтр по источнику (модулю, файлу)"""
    
    def __init__(self, include_patterns: List[str] | None = None, exclude_patterns: List[str] | None = None):
        """
        Args:
            include_patterns: Паттерны для включения
            exclude_patterns: Паттерны для исключения
        """
        super().__init__()
        self.include_patterns = [re.compile(p) for p in (include_patterns or [])]
        self.exclude_patterns = [re.compile(p) for p in (exclude_patterns or [])]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Фильтрация по источнику"""
        pathname = record.pathname
        
        # Если указаны паттерны включения, проверяем их
        if self.include_patterns:
            if not any(pattern.search(pathname) for pattern in self.include_patterns):
                return False
        
        # Если указаны паттерны исключения, проверяем их
        if self.exclude_patterns:
            if any(pattern.search(pathname) for pattern in self.exclude_patterns):
                return False
        
        return True


class ContentFilter(logging.Filter):
    """Фильтр по содержимому сообщения"""
    
    def __init__(self, 
                 include_patterns: List[str] | None = None,
                 exclude_patterns: List[str] | None = None,
                 case_sensitive: bool = True):
        """
        Args:
            include_patterns: Паттерны для включения
            exclude_patterns: Паттерны для исключения  
            case_sensitive: Учитывать регистр
        """
        super().__init__()
        flags = 0 if case_sensitive else re.IGNORECASE
        
        self.include_patterns = [re.compile(p, flags) for p in (include_patterns or [])]
        self.exclude_patterns = [re.compile(p, flags) for p in (exclude_patterns or [])]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Фильтрация по содержимому"""
        message = record.getMessage()
        
        if self.include_patterns:
            if not any(pattern.search(message) for pattern in self.include_patterns):
                return False
        
        if self.exclude_patterns:
            if any(pattern.search(message) for pattern in self.exclude_patterns):
                return False
        
        return True


class ThrottleFilter(logging.Filter):
    """Фильтр для ограничения частоты одинаковых сообщений"""
    
    def __init__(self, max_repeats: int = 10, time_window: int = 60):
        """
        Args:
            max_repeats: Максимальное количество повторений
            time_window: Временное окно в секундах
        """
        super().__init__()
        self.max_repeats = max_repeats
        self.time_window = time_window
        self.message_counts = {}
        self.message_times = {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Фильтрация с учетом частоты"""
        import time
        
        message_key = (record.name, record.getMessage())
        current_time = time.time()
        
        if message_key in self.message_times:
            old_times = [t for t in self.message_times[message_key] 
                        if current_time - t <= self.time_window]
            self.message_times[message_key] = old_times
        else:
            self.message_times[message_key] = []
        
        self.message_times[message_key].append(current_time)
        
        return len(self.message_times[message_key]) <= self.max_repeats 
    
