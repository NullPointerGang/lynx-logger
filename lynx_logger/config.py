"""
Конфигурация для LynxLogger
"""

import os
import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path


class Level(Enum):
    """Уровни логирования"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    @classmethod
    def from_string(cls, level: str) -> "Level":
        """Создает Level из строки"""
        try:
            return cls[level.upper()]
        except KeyError:
            raise ValueError(f"Неподдерживаемый уровень логирования: {level}")
    
    @property
    def value_int(self) -> int:
        """Возвращает числовое значение уровня"""
        return self.value


class Format(Enum):
    """Форматы логирования"""
    CONSOLE = "console"
    JSON = "json"
    KEYVALUE = "keyvalue"
    PLAIN = "plain"
    
    @classmethod
    def from_string(cls, format_str: str) -> "Format":
        """Создает Format из строки"""
        try:
            return cls(format_str.lower())
        except ValueError:
            raise ValueError(f"Неподдерживаемый формат логирования: {format_str}")


@dataclass
class FileConfig:
    """Конфигурация записи в файл"""
    enabled: bool = False
    filename: str = "app.log"
    max_size: str = "10MB"
    backup_count: int = 5
    encoding: str = "utf-8"
    delay: bool = False


@dataclass
class ConsoleConfig:
    """Конфигурация вывода в консоль"""
    enabled: bool = True
    colors: bool = True
    show_thread: bool = False
    show_process: bool = False
    pad_level: bool = True


@dataclass
class ContextConfig:
    """Конфигурация контекста"""
    include_caller: bool = False
    include_thread: bool = False
    include_process: bool = False
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FilterConfig:
    """Конфигурация фильтров"""
    min_level: Optional[Level] = None
    exclude_loggers: List[str] = field(default_factory=list)
    include_only: List[str] = field(default_factory=list)
    exclude_messages: List[str] = field(default_factory=list)


@dataclass
class LogConfig:
    """
    Основная конфигурация логгера
    
    Example:
        >>> config = LogConfig(
        ...     name="my_app",
        ...     level=Level.INFO,
        ...     format=Format.JSON,
        ...     file=FileConfig(enabled=True, filename="my_app.log"),
        ...     context=ContextConfig(include_caller=True)
        ... )
    """
    name: str = "trace"
    level: Level = Level.INFO
    format: Format = Format.CONSOLE
    dev_mode: bool = False
    
    log_to_console: bool = True
    log_to_file: bool = False
    logs_dir: str = "./logs"
    
    console: ConsoleConfig = field(default_factory=ConsoleConfig)
    file: FileConfig = field(default_factory=FileConfig)
    context: ContextConfig = field(default_factory=ContextConfig)
    filters: FilterConfig = field(default_factory=FilterConfig)
    
    extra_processors: List[Any] = field(default_factory=list)
    structured_logging: bool = True
    timestamp_format: str = "iso"
    exception_format: str = "short"
    
    def __post_init__(self):
        """Постобработка конфигурации"""
        if self.log_to_file:
            Path(self.logs_dir).mkdir(parents=True, exist_ok=True)
            self.file.enabled = True
        
        if self.log_to_console:
            self.console.enabled = True
        
        if self.dev_mode:
            self.console.colors = True
            self.context.include_caller = True
            if self.format == Format.CONSOLE:
                self.console.pad_level = True
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "LogConfig":
        """Создает конфигурацию из словаря"""
        if "console" in config_dict:
            config_dict["console"] = ConsoleConfig(**config_dict["console"])
        
        if "file" in config_dict:
            config_dict["file"] = FileConfig(**config_dict["file"])
        
        if "context" in config_dict:
            config_dict["context"] = ContextConfig(**config_dict["context"])
        
        if "filters" in config_dict:
            config_dict["filters"] = FilterConfig(**config_dict["filters"])
        
        if "level" in config_dict and isinstance(config_dict["level"], str):
            config_dict["level"] = Level.from_string(config_dict["level"])
        
        if "format" in config_dict and isinstance(config_dict["format"], str):
            config_dict["format"] = Format.from_string(config_dict["format"])
        
        return cls(**config_dict)
    
    @classmethod
    def from_env(cls, prefix: str = "LOG_") -> "LogConfig":
        """
        Создает конфигурацию из переменных окружения
        
        Example:
            Переменные окружения:
            LOG_NAME=my_app
            LOG_LEVEL=DEBUG
            LOG_FORMAT=json
            LOG_TO_FILE=true
            LOG_LOGS_DIR=/var/log/my_app
        """
        config = {}
        
        for key in ["name", "level", "format", "dev_mode", "log_to_console", "log_to_file", "logs_dir"]:
            env_key = f"{prefix}{key.upper()}"
            if env_value := os.getenv(env_key):
                if key in ["dev_mode", "log_to_console", "log_to_file"]:
                    config[key] = env_value.lower() in ("true", "1", "yes", "on")
                else:
                    config[key] = env_value
        
        return cls.from_dict(config)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует конфигурацию в словарь"""
        result = {}
        
        for key, value in self.__dict__.items():
            if isinstance(value, Enum):
                result[key] = value.value
            elif hasattr(value, '__dict__'):
                result[key] = value.__dict__
            else:
                result[key] = value
        
        return result
    
    @property
    def log_file_path(self) -> Optional[str]:
        """Полный путь к файлу логов"""
        if not self.file.enabled:
            return None
        return os.path.join(self.logs_dir, self.file.filename) 
    
