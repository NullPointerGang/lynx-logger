"""
Тесты модуля форматировщиков
"""

import pytest
import json
import logging
from lynx_logger.formatters import (
    ConsoleFormatter, JSONFormatter, KeyValueFormatter,
    get_formatter
)
from lynx_logger.config import Format


class TestConsoleFormatter:
    """Тесты для ConsoleFormatter"""
    
    def test_console_formatter_basic(self):
        """Тест базового форматирования консоли"""
        formatter = ConsoleFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.key1 = "value1"
        record.key2 = 123
        
        formatted = formatter.format(record)
        
        assert "Test message" in formatted
        assert "INFO" in formatted
        assert "test_logger" in formatted
        
    def test_console_formatter_with_colors(self):
        """Тест форматирования с цветами"""
        formatter = ConsoleFormatter(colors=True)
        
        record = logging.LogRecord(
            name="color_test",
            level=logging.ERROR,
            pathname="test.py", 
            lineno=1,
            msg="Error message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        assert "Error message" in formatted
        
    def test_console_formatter_without_colors(self):
        """Тест форматирования без цветов"""
        formatter = ConsoleFormatter(colors=False)
        
        record = logging.LogRecord(
            name="no_color_test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Warning message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        assert "Warning message" in formatted
        assert "WARNING" in formatted


class TestJSONFormatter:
    """Тесты для JSONFormatter"""
    
    def test_json_formatter_basic(self):
        """Тест базового JSON форматирования"""
        formatter = JSONFormatter()
        
        record = logging.LogRecord(
            name="json_test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="JSON test message",
            args=(),
            exc_info=None
        )

        record.user_id = 123
        record.action = "login"
        
        formatted = formatter.format(record)

        data = json.loads(formatted)
        
        assert data["event"] == "JSON test message"
        assert data["level"] == "info"
        assert data["logger"] == "json_test"
        assert "timestamp" in data
        
    def test_json_formatter_with_structured_data(self):
        """Тест JSON форматирования со структурированными данными"""
        formatter = JSONFormatter()
        
        record = logging.LogRecord(
            name="structured_test",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=20,
            msg="Structured message",
            args=(),
            exc_info=None
        )

        record.string_field = "test_string"
        record.int_field = 42
        record.float_field = 3.14
        record.bool_field = True
        record.list_field = [1, 2, 3]
        record.dict_field = {"nested": "value"}
        
        formatted = formatter.format(record)
        data = json.loads(formatted)
        
        assert data["string_field"] == "test_string"
        assert data["int_field"] == 42
        assert data["float_field"] == 3.14
        assert data["bool_field"] is True
        assert data["list_field"] == [1, 2, 3]
        assert data["dict_field"]["nested"] == "value"
        
    def test_json_formatter_with_exception(self):
        """Тест JSON форматирования с исключением"""
        formatter = JSONFormatter()
        
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            exc_info = (type(e), e, e.__traceback__)
            
        record = logging.LogRecord(
            name="exception_test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=30,
            msg="Exception occurred",
            args=(),
            exc_info=exc_info
        )
        
        formatted = formatter.format(record)
        data = json.loads(formatted)
        
        assert data["event"] == "Exception occurred"
        assert data["level"] == "error"
        assert "exception" in data or "exc_info" in data


class TestKeyValueFormatter:
    """Тесты для KeyValueFormatter"""
    
    def test_keyvalue_formatter_basic(self):
        """Тест базового key-value форматирования"""
        formatter = KeyValueFormatter()
        
        record = logging.LogRecord(
            name="kv_test",
            level=logging.INFO,
            pathname="test.py",
            lineno=40,
            msg="KeyValue test",
            args=(),
            exc_info=None
        )
        
        record.key1 = "value1"
        record.key2 = 42
        
        formatted = formatter.format(record)
        
        assert "event='KeyValue test'" in formatted
        assert "level='info'" in formatted  # KeyValueRenderer добавляет кавычки
        assert "logger='kv_test'" in formatted  # KeyValueRenderer добавляет кавычки
        assert "key1='value1'" in formatted  # KeyValueRenderer добавляет кавычки
        assert "key2=42" in formatted  # Числа без кавычек
        
    def test_keyvalue_formatter_special_characters(self):
        """Тест key-value форматирования со специальными символами"""
        formatter = KeyValueFormatter()
        
        record = logging.LogRecord(
            name="special_test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=50,
            msg="Test with spaces and quotes",
            args=(),
            exc_info=None
        )
        
        record.spaced_value = "value with spaces"
        record.quoted_value = 'value with "quotes"'
        
        formatted = formatter.format(record)
        
        assert "event='Test with spaces and quotes'" in formatted
        assert "spaced_value='value with spaces'" in formatted
        
    def test_keyvalue_formatter_none_values(self):
        """Тест key-value форматирования с None значениями"""
        formatter = KeyValueFormatter()
        
        record = logging.LogRecord(
            name="none_test",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=60,
            msg="None test",
            args=(),
            exc_info=None
        )
        
        record.none_value = None
        record.normal_value = "normal"
        
        formatted = formatter.format(record)
        
        assert "event='None test'" in formatted
        assert "none_value=None" in formatted or "none_value='None'" in formatted
        assert "normal_value='normal'" in formatted  # KeyValueRenderer добавляет кавычки


class TestGetFormatter:
    """Тесты для функции get_formatter"""
    
    def test_get_formatter_console(self):
        """Тест получения консольного форматировщика"""
        processors = []
        formatter = get_formatter(Format.CONSOLE, processors, colors=True, dev_mode=False)
        
        assert isinstance(formatter, logging.Formatter)
        
    def test_get_formatter_json(self):
        """Тест получения JSON форматировщика"""
        processors = []
        formatter = get_formatter(Format.JSON, processors, colors=False, dev_mode=False)
        
        assert isinstance(formatter, logging.Formatter)
        
    def test_get_formatter_keyvalue(self):
        """Тест получения KeyValue форматировщика"""
        processors = []
        formatter = get_formatter(Format.KEYVALUE, processors, colors=False, dev_mode=False)
        
        assert isinstance(formatter, logging.Formatter)
        
    def test_get_formatter_plain(self):
        """Тест получения Plain форматировщика"""
        processors = []
        formatter = get_formatter(Format.PLAIN, processors, colors=False, dev_mode=False)
        
        assert isinstance(formatter, logging.Formatter)
        
    def test_get_formatter_with_processors(self):
        """Тест получения форматировщика с процессорами"""
        def dummy_processor(logger, name, event_dict):
            return event_dict
            
        processors = [dummy_processor]
        formatter = get_formatter(Format.JSON, processors, colors=False, dev_mode=False)
        
        assert isinstance(formatter, logging.Formatter)
        
    def test_get_formatter_dev_mode(self):
        """Тест получения форматировщика в режиме разработки"""
        processors = []
        formatter = get_formatter(Format.CONSOLE, processors, colors=True, dev_mode=True)
        
        assert isinstance(formatter, logging.Formatter)
        
    def test_get_formatter_no_colors(self):
        """Тест получения форматировщика без цветов"""
        processors = []
        formatter = get_formatter(Format.CONSOLE, processors, colors=False, dev_mode=False)
        
        assert isinstance(formatter, logging.Formatter)


class TestFormatterIntegration:
    """Интеграционные тесты форматировщиков"""
    
    def test_formatter_with_real_logging(self):
        """Тест форматировщиков с реальным логированием"""
        import logging
        import io

        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        
        json_formatter = JSONFormatter()
        handler.setFormatter(json_formatter)
        
        logger = logging.getLogger("integration_test")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        extra = {"user_id": 123, "action": "test"}
        logger.info("Integration test message", extra=extra)
        
        output = log_stream.getvalue()
        
        try:
            data = json.loads(output.strip())
            assert data["event"] == "Integration test message"
            assert data["user_id"] == 123
            assert data["action"] == "test"
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")
        
        logger.removeHandler(handler)
        
    def test_multiple_formatters_same_message(self):
        """Тест одного сообщения с разными форматировщиками"""
        record = logging.LogRecord(
            name="multi_format_test",
            level=logging.INFO,
            pathname="test.py",
            lineno=100,
            msg="Multi format message",
            args=(),
            exc_info=None
        )
        
        record.test_field = "test_value"
        
        json_formatter = JSONFormatter()
        console_formatter = ConsoleFormatter()
        kv_formatter = KeyValueFormatter()
        
        json_output = json_formatter.format(record)
        console_output = console_formatter.format(record)
        kv_output = kv_formatter.format(record)

        json_data = json.loads(json_output)
        assert json_data["event"] == "Multi format message"
        
        assert "Multi format message" in console_output
        
        assert "event='Multi format message'" in kv_output
        
    def test_formatter_error_handling(self):
        """Тест обработки ошибок в форматировщиках"""
        formatter = JSONFormatter()
        
        record = logging.LogRecord(
            name="error_test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=200,
            msg="Error test",
            args=(),
            exc_info=None
        )
        
        class NonSerializable:
            def __str__(self):
                return "non_serializable_object"
                
        record.problem_field = NonSerializable()
        
        formatted = formatter.format(record)
        
        assert isinstance(formatted, str)
        assert len(formatted) > 0 

    