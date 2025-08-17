"""
Тесты основного модуля LynxLogger
"""

import tempfile
import shutil
import os
import logging
from lynx_logger import LynxLogger, LogConfig, Level, Format
from lynx_logger.config import FileConfig


class TestLynxLogger:
    """Тесты для класса LynxLogger"""
    
    def setup_method(self):
        """Подготовка к каждому тесту"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Очистка после каждого теста"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
    def test_logger_initialization(self):
        """Тест инициализации логгера"""
        config = LogConfig(
            name="test_logger",
            level=Level.DEBUG,
            format=Format.CONSOLE,
            log_to_console=True,
            log_to_file=False
        )
        
        logger = LynxLogger(config)
        
        assert logger.config == config
        assert logger.get_logger() is not None
        assert logger.config.name == "test_logger"
        assert logger.config.level == Level.DEBUG
        
    def test_console_logging(self, capfd):
        """Тест логирования в консоль"""
        config = LogConfig(
            name="console_test",
            level=Level.INFO,
            format=Format.CONSOLE,
            log_to_console=True,
            log_to_file=False,
            dev_mode=False
        )
        
        logger = LynxLogger(config)
        logger.info("Test message", test_key="test_value")
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert "Test message" in output
        assert "test_key" in output and "test_value" in output
        
    def test_file_logging(self):
        """Тест логирования в файл"""
        log_file = os.path.join(self.temp_dir, "test.log")
        
        config = LogConfig(
            name="file_test",
            level=Level.INFO,
            format=Format.JSON,
            log_to_console=False,
            log_to_file=True,
            logs_dir=self.temp_dir,
            file=FileConfig(filename="test.log")
        )
        
        logger = LynxLogger(config)
        logger.info("File test message", test_field="file_value")

        for handler in logging.getLogger().handlers:
            handler.flush()
        
        assert os.path.exists(log_file)
        with open(log_file, 'r') as f:
            content = f.read()
            assert "File test message" in content
            assert "file_value" in content
            
    def test_json_format(self, capfd):
        """Тест JSON формата"""
        config = LogConfig(
            name="json_test",
            level=Level.INFO,
            format=Format.JSON,
            log_to_console=True,
            log_to_file=False
        )
        
        logger = LynxLogger(config)
        logger.info("JSON test", number=42, boolean=True)
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert '"event": "JSON test"' in output
        assert '"number": 42' in output
        assert '"boolean": true' in output
        
    def test_logging_levels(self, capfd):
        """Тест различных уровней логирования"""
        config = LogConfig(
            name="level_test",
            level=Level.DEBUG,
            format=Format.CONSOLE,
            log_to_console=True,
            log_to_file=False
        )
        
        logger = LynxLogger(config)
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert "Debug message" in output
        assert "Info message" in output
        assert "Warning message" in output
        assert "Error message" in output
        assert "Critical message" in output
        
    def test_bind_context(self, capfd):
        """Тест привязки контекста"""
        config = LogConfig(
            name="bind_test",
            level=Level.INFO,
            format=Format.CONSOLE,
            log_to_console=True,
            log_to_file=False,
            dev_mode=False
        )
        
        logger = LynxLogger(config)
        bound_logger = logger.bind(user_id="123", session_id="abc")
        bound_logger.info("Bound message")
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert "user_id" in output and "123" in output
        assert "session_id" in output and "abc" in output
        assert "Bound message" in output
        
    def test_exception_logging(self, capfd):
        """Тест логирования исключений"""
        config = LogConfig(
            name="exception_test",
            level=Level.ERROR,
            format=Format.CONSOLE,
            log_to_console=True,
            log_to_file=False
        )
        
        logger = LynxLogger(config)
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("Exception occurred")
            
        captured = capfd.readouterr()
        output = captured.out
        
        assert "Exception occurred" in output
        assert "ValueError" in output
        assert "Test exception" in output
        
    def test_context_manager(self, capfd):
        """Тест использования как контекстный менеджер"""
        config = LogConfig(
            name="context_test",
            level=Level.INFO,
            format=Format.CONSOLE,
            log_to_console=True,
            log_to_file=False
        )
        
        with LynxLogger(config) as logger:
            logger.info("Inside context manager")
            
        captured = capfd.readouterr()
        assert "Inside context manager" in captured.out
        
    def test_context_manager_with_exception(self, capfd):
        """Тест контекстного менеджера с исключением"""
        config = LogConfig(
            name="context_exception_test",
            level=Level.INFO,
            format=Format.CONSOLE,
            log_to_console=True,
            log_to_file=False
        )
        
        try:
            with LynxLogger(config) as logger:
                logger.info("Before exception")
                raise RuntimeError("Test error")
        except RuntimeError:
            pass
            
        captured = capfd.readouterr()
        output = captured.out
        
        assert "Before exception" in output
        assert "Exception in logger context" in output
        
    def test_level_change(self, capfd):
        """Тест изменения уровня логирования"""
        config = LogConfig(
            name="level_change_test",
            level=Level.INFO,
            format=Format.CONSOLE,
            log_to_console=True,
            log_to_file=False
        )
        
        logger = LynxLogger(config)
        
        logger.debug("Debug before level change")
        
        logger.set_level(Level.DEBUG)
        
        logger.debug("Debug after level change")
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert "Debug before level change" not in output
        assert "Debug after level change" in output
        assert "Log level changed" in output
        
    def test_config_reload(self, capfd):
        """Тест перезагрузки конфигурации"""
        config1 = LogConfig(
            name="reload_test_1",
            level=Level.INFO,
            format=Format.CONSOLE,
            log_to_console=True,
            log_to_file=False
        )
        
        config2 = LogConfig(
            name="reload_test_2", 
            level=Level.DEBUG,
            format=Format.JSON,
            log_to_console=True,
            log_to_file=False
        )
        
        logger = LynxLogger(config1)
        logger.info("Before reload")
        
        logger.reload_config(config2)
        logger.debug("After reload")
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert "Before reload" in output
        assert "Logger configuration reloaded" in output
        assert "After reload" in output
        
    def test_get_config(self):
        """Тест получения конфигурации"""
        config = LogConfig(
            name="config_test",
            level=Level.WARNING,
            format=Format.KEYVALUE
        )
        
        logger = LynxLogger(config)
        retrieved_config = logger.get_config()
        
        assert retrieved_config == config
        assert retrieved_config.name == "config_test"
        assert retrieved_config.level == Level.WARNING
        assert retrieved_config.format == Format.KEYVALUE
        
    def test_file_rotation_config(self):
        """Тест конфигурации ротации файлов"""
        config = LogConfig(
            name="rotation_test",
            log_to_file=True,
            logs_dir=self.temp_dir,
            file=FileConfig(
                filename="rotation.log",
                max_size="1KB",
                backup_count=3
            )
        )
        
        logger = LynxLogger(config)
        
        for i in range(100):
            logger.info(f"Log message number {i} with some additional data to increase size")
        
        for handler in logging.getLogger().handlers:
            handler.flush()
        
        log_file = os.path.join(self.temp_dir, "rotation.log")
        assert os.path.exists(log_file)
        
    def test_dev_mode_settings(self):
        """Тест настроек режима разработки"""
        config = LogConfig(
            name="dev_test",
            dev_mode=True,
            log_to_console=True
        )
        
        logger = LynxLogger(config)
        
        assert config.console.colors is True
        assert config.context.include_caller is True
        
    def test_with_context_alias(self, capfd):
        """Тест алиаса with_context"""
        config = LogConfig(
            name="alias_test",
            level=Level.INFO,
            format=Format.CONSOLE,
            log_to_console=True,
            log_to_file=False,
            dev_mode=False
        )
        
        logger = LynxLogger(config)
        context_logger = logger.with_context(operation="test_op")
        context_logger.info("Context alias test")
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert "operation" in output and "test_op" in output
        assert "Context alias test" in output
        
    def test_warn_alias(self, capfd):
        """Тест алиаса warn для warning"""
        config = LogConfig(
            name="warn_test",
            level=Level.WARNING,
            format=Format.CONSOLE,
            log_to_console=True,
            log_to_file=False
        )
        
        logger = LynxLogger(config)
        logger.warn("Warning via warn alias")
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert "Warning via warn alias" in output
        
    def test_log_with_level_enum(self, capfd):
        """Тест метода log с Level enum"""
        config = LogConfig(
            name="log_enum_test",
            level=Level.DEBUG,
            format=Format.CONSOLE,
            log_to_console=True,
            log_to_file=False
        )
        
        logger = LynxLogger(config)
        logger.log(Level.INFO, "Log with enum level")
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert "Log with enum level" in output
        
    def test_log_with_int_level(self, capfd):
        """Тест метода log с числовым уровнем"""
        config = LogConfig(
            name="log_int_test",
            level=Level.DEBUG,
            format=Format.CONSOLE,
            log_to_console=True,
            log_to_file=False
        )
        
        logger = LynxLogger(config)
        logger.log(logging.ERROR, "Log with int level")
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert "Log with int level" in output 

