"""
Форматировщики для различных типов вывода
"""

import structlog
from typing import List, Any, Optional
from .config import Format


class ConsoleFormatter:
    """Форматировщик для консольного вывода"""
    
    @staticmethod
    def create(colors: bool = True, pad_level: bool = True, dev_mode: bool = False):
        """Создает процессор для консольного вывода"""
        return structlog.dev.ConsoleRenderer(
            colors=colors,
            pad_level=pad_level,
            level_styles={
                "critical": "\033[1;31m",  # Яркий красный
                "error": "\033[31m",       # Красный
                "warning": "\033[33m",     # Желтый
                "info": "\033[32m",        # Зеленый
                "debug": "\033[36m",       # Голубой
            } if colors else None,
            exception_formatter=structlog.dev.rich_traceback if dev_mode else structlog.dev.plain_traceback
        )


class JSONFormatter:
    """Форматировщик для JSON вывода"""
    
    @staticmethod
    def create(sort_keys: bool = False, indent: Optional[int] = None):
        """Создает процессор для JSON вывода"""
        return structlog.processors.JSONRenderer(
            sort_keys=sort_keys,
            indent=indent
        )


class KeyValueFormatter:
    """Форматировщик для key=value вывода"""
    
    @staticmethod
    def create(key_order: Optional[List[str]] = None, drop_missing: bool = False):
        """Создает процессор для key=value вывода"""
        return structlog.processors.KeyValueRenderer(
            key_order=key_order or ["timestamp", "level", "logger", "event"],
            drop_missing=drop_missing
        )


class PlainFormatter:
    """Простой текстовый форматировщик"""
    
    @staticmethod
    def create():
        """Создает простой текстовый процессор"""
        def plain_formatter(logger, name, event_dict):
            """Простое форматирование сообщения"""
            timestamp = event_dict.get("timestamp", "")
            level = event_dict.get("level", "").upper()
            logger_name = event_dict.get("logger", "")
            event = event_dict.get("event", "")
            
            extra_fields = []
            for key, value in event_dict.items():
                if key not in ("timestamp", "level", "logger", "event"):
                    extra_fields.append(f"{key}={value}")
            
            extra_str = " " + " ".join(extra_fields) if extra_fields else ""
            
            return f"{timestamp} [{level}] {logger_name}: {event}{extra_str}"
        
        return plain_formatter


def get_formatter(
    format_type: Format,
    shared_processors: List[Any],
    colors: bool = True,
    dev_mode: bool = False
) -> structlog.stdlib.ProcessorFormatter:
    """
    Создает форматировщик на основе типа формата
    
    Args:
        format_type: Тип формата (CONSOLE, JSON, KEYVALUE, PLAIN)
        shared_processors: Общие процессоры
        colors: Включить цвета (только для CONSOLE)
        dev_mode: Режим разработки
    
    Returns:
        Настроенный ProcessorFormatter
    """
    if format_type == Format.CONSOLE:
        processor = ConsoleFormatter.create(colors=colors, dev_mode=dev_mode)
    elif format_type == Format.JSON:
        processor = JSONFormatter.create()
    elif format_type == Format.KEYVALUE:
        processor = KeyValueFormatter.create()
    elif format_type == Format.PLAIN:
        processor = PlainFormatter.create()
    else:
        raise ValueError(f"Неподдерживаемый формат: {format_type}")
    
    return structlog.stdlib.ProcessorFormatter(
        processor=processor,
        foreign_pre_chain=shared_processors,
    ) 

