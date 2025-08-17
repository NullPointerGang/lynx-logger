"""
Тесты для функции setup_logger
"""

import pytest
import tempfile
import shutil
import logging
import os

from lynx_logger import setup_logger, LynxLogger, Level, Format


class TestSetupLogger:
    """Тесты для функции setup_logger"""
    
    def setup_method(self):
        """Подготовка к каждому тесту"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Очистка после каждого теста"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
    def test_default_parameters(self):
        """Тест с параметрами по умолчанию"""
        logger = setup_logger()
        
        assert isinstance(logger, LynxLogger)
        assert logger.config.name == "lynx"
        assert logger.config.level == Level.INFO
        assert logger.config.format == Format.CONSOLE
        assert logger.config.dev_mode is False
        assert logger.config.log_to_console is True
        assert logger.config.log_to_file is False
        assert logger.config.logs_dir == "./logs"
        
    def test_custom_name(self):
        """Тест с пользовательским именем"""
        logger = setup_logger("my_custom_app")
        
        assert logger.config.name == "my_custom_app"
        
    def test_custom_level_string(self):
        """Тест с пользовательским уровнем (строка)"""
        test_cases = [
            ("DEBUG", Level.DEBUG),
            ("INFO", Level.INFO),
            ("WARNING", Level.WARNING),
            ("ERROR", Level.ERROR),
            ("CRITICAL", Level.CRITICAL),
            ("debug", Level.DEBUG),
            ("Warning", Level.WARNING)
        ]
        
        for level_str, expected_level in test_cases:
            logger = setup_logger(level=level_str)
            assert logger.config.level == expected_level
            
    def test_custom_format_string(self):
        """Тест с пользовательским форматом (строка)"""
        test_cases = [
            ("console", Format.CONSOLE),
            ("json", Format.JSON),
            ("keyvalue", Format.KEYVALUE),
            ("plain", Format.PLAIN),
            ("JSON", Format.JSON),
            ("Console", Format.CONSOLE)
        ]
        
        for format_str, expected_format in test_cases:
            logger = setup_logger(format=format_str)
            assert logger.config.format == expected_format
            
    def test_dev_mode_enabled(self):
        """Тест режима разработки"""
        logger = setup_logger(dev_mode=True)
        
        assert logger.config.dev_mode is True
        assert logger.config.console.colors is True
        assert logger.config.context.include_caller is True
        
    def test_console_logging_disabled(self):
        """Тест отключения консольного логирования"""
        logger = setup_logger(log_to_console=False)
        
        assert logger.config.log_to_console is False
        
    def test_file_logging_enabled(self):
        """Тест включения файлового логирования"""
        logger = setup_logger(
            log_to_file=True,
            logs_dir=self.temp_dir
        )
        
        assert logger.config.log_to_file is True
        assert logger.config.logs_dir == self.temp_dir
        assert logger.config.file.enabled is True
        assert os.path.exists(self.temp_dir)
        
    def test_custom_logs_dir(self):
        """Тест пользовательской директории для логов"""
        custom_dir = os.path.join(self.temp_dir, "custom_logs")
        logger = setup_logger(
            log_to_file=True,
            logs_dir=custom_dir
        )
        
        assert logger.config.logs_dir == custom_dir
        assert os.path.exists(custom_dir)
        
    def test_all_parameters(self):
        """Тест с все параметрами"""
        logger = setup_logger(
            name="full_test",
            level="DEBUG",
            format="json",
            dev_mode=True,
            log_to_console=True,
            log_to_file=True,
            logs_dir=self.temp_dir
        )
        
        assert logger.config.name == "full_test"
        assert logger.config.level == Level.DEBUG
        assert logger.config.format == Format.JSON
        assert logger.config.dev_mode is True
        assert logger.config.log_to_console is True
        assert logger.config.log_to_file is True
        assert logger.config.logs_dir == self.temp_dir
        
    def test_kwargs_passed_to_config(self):
        """Тест передачи дополнительных параметров в LogConfig"""
        logger = setup_logger(
            name="kwargs_test",
            timestamp_format="unix",
            exception_format="full",
            structured_logging=False
        )
        
        assert logger.config.name == "kwargs_test"
        assert logger.config.timestamp_format == "unix"
        assert logger.config.exception_format == "full"
        assert logger.config.structured_logging is False
        
    def test_logger_functionality(self, capfd):
        """Тест что созданный логгер действительно работает"""
        logger = setup_logger(
            name="functional_test",
            level="INFO",
            format="console",
            log_to_console=True,
            log_to_file=False,
            dev_mode=False
        )
        
        logger.info("Test message from setup_logger", test=True)
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert "Test message from setup_logger" in output
        assert "test" in output and "True" in output
        
    def test_file_logging_functionality(self):
        """Тест файлового логирования"""
        log_file_path = os.path.join(self.temp_dir, "app.log")
        
        logger = setup_logger(
            name="file_functional_test",
            format="json",
            log_to_console=False,
            log_to_file=True,
            logs_dir=self.temp_dir
        )
        
        logger.info("File test message", file_test=True)
        
        for handler in logging.getLogger().handlers:
            handler.flush()
            
        assert os.path.exists(log_file_path)
        with open(log_file_path, 'r') as f:
            content = f.read()
            assert "File test message" in content
            assert "file_test" in content
            
    def test_multiple_loggers_same_name(self):
        """Тест создания нескольких логгеров с одним именем"""
        logger1 = setup_logger("same_name", level="INFO")
        logger2 = setup_logger("same_name", level="DEBUG")
        
        assert isinstance(logger1, LynxLogger)
        assert isinstance(logger2, LynxLogger)
        assert logger1.config.name == "same_name"
        assert logger2.config.name == "same_name"
        
    def test_multiple_loggers_different_names(self):
        """Тест создания нескольких логгеров с разными именами"""
        logger1 = setup_logger("app1", level="INFO")
        logger2 = setup_logger("app2", level="DEBUG")
        
        assert logger1.config.name == "app1"
        assert logger2.config.name == "app2"
        assert logger1.config.level == Level.INFO
        assert logger2.config.level == Level.DEBUG
        
    def test_invalid_level(self):
        """Тест с невалидным уровнем логирования"""
        with pytest.raises(ValueError, match="Неподдерживаемый уровень логирования"):
            setup_logger(level="INVALID_LEVEL")
            
    def test_invalid_format(self):
        """Тест с невалидным форматом"""
        with pytest.raises(ValueError, match="Неподдерживаемый формат логирования"):
            setup_logger(format="invalid_format")
            
    def test_edge_cases(self):
        """Тест граничных случаев"""
        logger = setup_logger("")
        assert logger.config.name == ""
        
        logger = setup_logger(
            log_to_console=False, 
            log_to_file=False
        )
        assert logger.config.log_to_console is False
        assert logger.config.log_to_file is False
        
    def test_return_type(self):
        """Тест типа возвращаемого значения"""
        logger = setup_logger("type_test")
        
        assert isinstance(logger, LynxLogger)
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'critical')
        assert hasattr(logger, 'exception')
        assert hasattr(logger, 'bind')
        assert hasattr(logger, 'get_logger')
        
    def test_complex_setup(self, capfd):
        """Тест сложной настройки через setup_logger"""
        logger = setup_logger(
            name="complex_setup",
            level="DEBUG",
            format="keyvalue",
            dev_mode=False,
            log_to_console=True,
            log_to_file=True,
            logs_dir=self.temp_dir,
            timestamp_format="iso",
            structured_logging=True
        )
        
        logger.debug("Debug message")
        logger.info("Info message", key="value")
        logger.warning("Warning message")
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert "Debug message" in output
        assert "Info message" in output
        assert "Warning message" in output
        assert "key='value'" in output
        
    def test_directory_creation(self):
        """Тест создания директории для логов"""
        nested_dir = os.path.join(self.temp_dir, "nested", "logs", "dir")
        
        logger = setup_logger(
            log_to_file=True,
            logs_dir=nested_dir
        )
        
        assert os.path.exists(nested_dir)
        assert logger.config.logs_dir == nested_dir 

