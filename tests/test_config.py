"""
Тесты модуля конфигурации
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch

from lynx_logger.config import (
    LogConfig, Level, Format, 
    FileConfig, ConsoleConfig, ContextConfig, FilterConfig
)


class TestLevel:
    """Тесты для enum Level"""
    
    def test_level_values(self):
        """Тест значений уровней"""
        assert Level.DEBUG.value == 10
        assert Level.INFO.value == 20
        assert Level.WARNING.value == 30
        assert Level.ERROR.value == 40
        assert Level.CRITICAL.value == 50
        
    def test_from_string_valid(self):
        """Тест создания Level из строки - валидные значения"""
        assert Level.from_string("DEBUG") == Level.DEBUG
        assert Level.from_string("info") == Level.INFO
        assert Level.from_string("Warning") == Level.WARNING
        assert Level.from_string("ERROR") == Level.ERROR
        assert Level.from_string("critical") == Level.CRITICAL
        
    def test_from_string_invalid(self):
        """Тест создания Level из строки - невалидные значения"""
        with pytest.raises(ValueError, match="Неподдерживаемый уровень логирования: INVALID"):
            Level.from_string("INVALID")
            
    def test_value_int_property(self):
        """Тест свойства value_int"""
        assert Level.DEBUG.value_int == 10
        assert Level.INFO.value_int == 20


class TestFormat:
    """Тесты для enum Format"""
    
    def test_format_values(self):
        """Тест значений форматов"""
        assert Format.CONSOLE.value == "console"
        assert Format.JSON.value == "json"
        assert Format.KEYVALUE.value == "keyvalue"
        assert Format.PLAIN.value == "plain"
        
    def test_from_string_valid(self):
        """Тест создания Format из строки - валидные значения"""
        assert Format.from_string("console") == Format.CONSOLE
        assert Format.from_string("JSON") == Format.JSON
        assert Format.from_string("KeyValue") == Format.KEYVALUE
        assert Format.from_string("plain") == Format.PLAIN
        
    def test_from_string_invalid(self):
        """Тест создания Format из строки - невалидные значения"""
        with pytest.raises(ValueError, match="Неподдерживаемый формат логирования: xml"):
            Format.from_string("xml")


class TestFileConfig:
    """Тесты для FileConfig"""
    
    def test_default_values(self):
        """Тест значений по умолчанию"""
        config = FileConfig()
        
        assert config.enabled is False
        assert config.filename == "app.log"
        assert config.max_size == "10MB"
        assert config.backup_count == 5
        assert config.encoding == "utf-8"
        assert config.delay is False
        
    def test_custom_values(self):
        """Тест пользовательских значений"""
        config = FileConfig(
            enabled=True,
            filename="custom.log",
            max_size="50MB",
            backup_count=10,
            encoding="cp1251",
            delay=True
        )
        
        assert config.enabled is True
        assert config.filename == "custom.log"
        assert config.max_size == "50MB"
        assert config.backup_count == 10
        assert config.encoding == "cp1251"
        assert config.delay is True


class TestConsoleConfig:
    """Тесты для ConsoleConfig"""
    
    def test_default_values(self):
        """Тест значений по умолчанию"""
        config = ConsoleConfig()
        
        assert config.enabled is True
        assert config.colors is True
        assert config.show_thread is False
        assert config.show_process is False
        assert config.pad_level is True
        
    def test_custom_values(self):
        """Тест пользовательских значений"""
        config = ConsoleConfig(
            enabled=False,
            colors=False,
            show_thread=True,
            show_process=True,
            pad_level=False
        )
        
        assert config.enabled is False
        assert config.colors is False
        assert config.show_thread is True
        assert config.show_process is True
        assert config.pad_level is False


class TestContextConfig:
    """Тесты для ContextConfig"""
    
    def test_default_values(self):
        """Тест значений по умолчанию"""
        config = ContextConfig()
        
        assert config.include_caller is False
        assert config.include_thread is False
        assert config.include_process is False
        assert config.custom_fields == {}
        
    def test_custom_values(self):
        """Тест пользовательских значений"""
        custom_fields = {"app_name": "test_app", "version": "1.0"}
        config = ContextConfig(
            include_caller=True,
            include_thread=True,
            include_process=True,
            custom_fields=custom_fields
        )
        
        assert config.include_caller is True
        assert config.include_thread is True
        assert config.include_process is True
        assert config.custom_fields == custom_fields


class TestFilterConfig:
    """Тесты для FilterConfig"""
    
    def test_default_values(self):
        """Тест значений по умолчанию"""
        config = FilterConfig()
        
        assert config.min_level is None
        assert config.exclude_loggers == []
        assert config.include_only == []
        assert config.exclude_messages == []
        
    def test_custom_values(self):
        """Тест пользовательских значений"""
        config = FilterConfig(
            min_level=Level.WARNING,
            exclude_loggers=["urllib3", "requests"],
            include_only=["myapp"],
            exclude_messages=["health.*", "ping"]
        )
        
        assert config.min_level == Level.WARNING
        assert config.exclude_loggers == ["urllib3", "requests"]
        assert config.include_only == ["myapp"]
        assert config.exclude_messages == ["health.*", "ping"]


class TestLogConfig:
    """Тесты для основного класса LogConfig"""
    
    def setup_method(self):
        """Подготовка к каждому тесту"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Очистка после каждого теста"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_values(self):
        """Тест значений по умолчанию"""
        config = LogConfig()
        
        assert config.name == "trace"
        assert config.level == Level.INFO
        assert config.format == Format.CONSOLE
        assert config.dev_mode is False
        assert config.log_to_console is True
        assert config.log_to_file is False
        assert config.logs_dir == "./logs"
        assert isinstance(config.console, ConsoleConfig)
        assert isinstance(config.file, FileConfig)
        assert isinstance(config.context, ContextConfig)
        assert isinstance(config.filters, FilterConfig)
        assert config.extra_processors == []
        assert config.structured_logging is True
        assert config.timestamp_format == "iso"
        assert config.exception_format == "short"
        
    def test_custom_values(self):
        """Тест пользовательских значений"""
        console_config = ConsoleConfig(colors=False)
        file_config = FileConfig(enabled=True, filename="custom.log")
        
        config = LogConfig(
            name="custom_app",
            level=Level.DEBUG,
            format=Format.JSON,
            dev_mode=True,
            log_to_console=False,
            log_to_file=True,
            logs_dir="/var/log",
            console=console_config,
            file=file_config,
            timestamp_format="unix"
        )
        
        assert config.name == "custom_app"
        assert config.level == Level.DEBUG
        assert config.format == Format.JSON
        assert config.dev_mode is True
        assert config.log_to_console is False
        assert config.log_to_file is True
        assert config.logs_dir == "/var/log"
        assert config.console == console_config
        assert config.file == file_config
        assert config.timestamp_format == "unix"
        
    def test_post_init_file_creation(self):
        """Тест создания директории для файлов в __post_init__"""
        log_dir = os.path.join(self.temp_dir, "test_logs")
        config = LogConfig(
            log_to_file=True,
            logs_dir=log_dir
        )
        
        assert os.path.exists(log_dir)
        assert config.file.enabled is True
        
    def test_post_init_console_enabled(self):
        """Тест включения консоли в __post_init__"""
        config = LogConfig(log_to_console=True)
        assert config.console.enabled is True
        
    def test_post_init_dev_mode(self):
        """Тест настроек dev_mode в __post_init__"""
        config = LogConfig(dev_mode=True, format=Format.CONSOLE)
        
        assert config.console.colors is True
        assert config.context.include_caller is True
        assert config.console.pad_level is True
        
    def test_from_dict_simple(self):
        """Тест создания из простого словаря"""
        config_dict = {
            "name": "test_from_dict",
            "level": "DEBUG",
            "format": "json",
            "dev_mode": True
        }
        
        config = LogConfig.from_dict(config_dict)
        
        assert config.name == "test_from_dict"
        assert config.level == Level.DEBUG
        assert config.format == Format.JSON
        assert config.dev_mode is True
        
    def test_from_dict_nested(self):
        """Тест создания из вложенного словаря"""
        config_dict = {
            "name": "nested_test",
            "level": "INFO",
            "format": "console",
            "console": {
                "colors": False,
                "show_thread": True
            },
            "file": {
                "enabled": True,
                "filename": "nested.log",
                "max_size": "20MB"
            },
            "context": {
                "include_caller": True,
                "custom_fields": {"service": "test"}
            },
            "filters": {
                "min_level": "WARNING",
                "exclude_loggers": ["test"]
            }
        }
        
        config = LogConfig.from_dict(config_dict)
        
        assert config.name == "nested_test"
        assert config.level == Level.INFO
        assert config.format == Format.CONSOLE
        assert config.console.colors is False
        assert config.console.show_thread is True
        assert config.file.enabled is True
        assert config.file.filename == "nested.log"
        assert config.file.max_size == "20MB"
        assert config.context.include_caller is True
        assert config.context.custom_fields == {"service": "test"}
        
    def test_from_env_basic(self):
        """Тест создания из переменных окружения - базовый случай"""
        env_vars = {
            "LOG_NAME": "env_test",
            "LOG_LEVEL": "ERROR",
            "LOG_FORMAT": "json",
            "LOG_DEV_MODE": "true",
            "LOG_LOG_TO_CONSOLE": "false",
            "LOG_LOG_TO_FILE": "true",
            "LOG_LOGS_DIR": "/tmp/logs"
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            config = LogConfig.from_env()
            
        assert config.name == "env_test"
        assert config.level == Level.ERROR
        assert config.format == Format.JSON
        assert config.dev_mode is True
        assert config.log_to_console is False
        assert config.log_to_file is True
        assert config.logs_dir == "/tmp/logs"
        
    def test_from_env_custom_prefix(self):
        """Тест создания из переменных окружения с кастомным префиксом"""
        env_vars = {
            "MYAPP_NAME": "custom_prefix",
            "MYAPP_LEVEL": "DEBUG"
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            config = LogConfig.from_env(prefix="MYAPP_")
            
        assert config.name == "custom_prefix"
        assert config.level == Level.DEBUG
        
    def test_from_env_boolean_values(self):
        """Тест парсинга булевых значений из переменных окружения"""
        test_cases = [
            ("true", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("TRUE", True),
            ("false", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("FALSE", False)
        ]
        
        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"LOG_DEV_MODE": env_value}, clear=False):
                config = LogConfig.from_env()
                assert config.dev_mode == expected, f"Failed for {env_value}"
                
    def test_to_dict(self):
        """Тест преобразования в словарь"""
        config = LogConfig(
            name="to_dict_test",
            level=Level.WARNING,
            format=Format.KEYVALUE,
            dev_mode=True
        )
        
        result = config.to_dict()
        
        assert result["name"] == "to_dict_test"
        assert result["level"] == 30  # WARNING.value
        assert result["format"] == "keyvalue"
        assert result["dev_mode"] is True
        assert "console" in result
        assert "file" in result
        assert isinstance(result["console"], dict)
        assert isinstance(result["file"], dict)
        
    def test_log_file_path_enabled(self):
        """Тест получения пути к файлу логов - включен"""
        config = LogConfig(
            log_to_file=True,
            logs_dir="/var/log",
            file=FileConfig(filename="test.log")
        )
        
        expected_path = "/var/log/test.log"
        assert config.log_file_path == expected_path
        
    def test_log_file_path_disabled(self):
        """Тест получения пути к файлу логов - выключен"""
        config = LogConfig(log_to_file=False)
        
        assert config.log_file_path is None
        
    def test_complex_configuration(self):
        """Тест сложной конфигурации"""
        custom_processors = [lambda: None, lambda: None]
        
        config = LogConfig(
            name="complex_app",
            level=Level.DEBUG,
            format=Format.JSON,
            dev_mode=True,
            log_to_console=True,
            log_to_file=True,
            logs_dir=self.temp_dir,
            console=ConsoleConfig(
                colors=True,
                show_thread=True,
                show_process=True
            ),
            file=FileConfig(
                filename="complex.log",
                max_size="50MB",
                backup_count=10
            ),
            context=ContextConfig(
                include_caller=True,
                include_thread=True,
                custom_fields={"app": "complex", "version": "1.0"}
            ),
            filters=FilterConfig(
                min_level=Level.INFO,
                exclude_loggers=["urllib3"],
                exclude_messages=["health"]
            ),
            extra_processors=custom_processors,
            timestamp_format="unix",
            exception_format="full"
        )
        
        assert config.name == "complex_app"
        assert config.level == Level.DEBUG
        assert config.format == Format.JSON
        assert config.dev_mode is True
        assert config.console.show_thread is True
        assert config.file.max_size == "50MB"
        assert config.context.custom_fields["app"] == "complex"
        assert config.filters.exclude_loggers == ["urllib3"]
        assert config.extra_processors == custom_processors
        assert config.timestamp_format == "unix"
        assert config.exception_format == "full"
        
        assert os.path.exists(self.temp_dir)
        assert config.file.enabled is True 