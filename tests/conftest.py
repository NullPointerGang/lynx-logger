"""
Конфигурация тестов для LynxLogger
"""

import pytest
import logging
import tempfile
import shutil
from pathlib import Path

from lynx_logger import LynxLogger, LogConfig, Level, Format


@pytest.fixture
def temp_dir():
    """Фикстура для создания временной директории"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def clean_logging():
    """Фикстура для очистки logging handlers между тестами"""
    # Сохраняем текущие handlers
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    original_level = root_logger.level
    
    yield
    
    # Очищаем добавленные handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()
    
    # Восстанавливаем оригинальные
    for handler in original_handlers:
        root_logger.addHandler(handler)
    
    root_logger.setLevel(original_level)


@pytest.fixture
def basic_config():
    """Фикстура базовой конфигурации"""
    return LogConfig(
        name="test_logger",
        level=Level.DEBUG,
        format=Format.CONSOLE,
        log_to_console=True,
        log_to_file=False,
        dev_mode=False
    )


@pytest.fixture
def json_config():
    """Фикстура JSON конфигурации"""
    return LogConfig(
        name="json_test_logger",
        level=Level.INFO,
        format=Format.JSON,
        log_to_console=True,
        log_to_file=False,
        dev_mode=False
    )


@pytest.fixture
def file_config(temp_dir):
    """Фикстура файловой конфигурации"""
    return LogConfig(
        name="file_test_logger", 
        level=Level.INFO,
        format=Format.JSON,
        log_to_console=False,
        log_to_file=True,
        logs_dir=temp_dir
    )


@pytest.fixture  
def basic_logger(basic_config, clean_logging):
    """Фикстура базового логгера"""
    return LynxLogger(basic_config)


@pytest.fixture
def json_logger(json_config, clean_logging):
    """Фикстура JSON логгера"""
    return LynxLogger(json_config)


@pytest.fixture
def file_logger(file_config, clean_logging):
    """Фикстура файлового логгера"""
    return LynxLogger(file_config)


@pytest.fixture
def sample_log_data():
    """Фикстура с образцами данных для логирования"""
    return {
        "user_id": 12345,
        "session_id": "sess_abcdef123456",
        "request_id": "req_789xyz",
        "action": "user_login",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 Test Agent",
        "timestamp": "2025-01-16T10:30:45Z",
        "success": True,
        "duration_ms": 150.5
    }


# Параметризованные фикстуры для тестирования разных форматов
@pytest.fixture(params=[Format.CONSOLE, Format.JSON, Format.KEYVALUE])
def format_config(request, temp_dir):
    """Параметризованная фикстура для разных форматов"""
    return LogConfig(
        name="format_test_logger",
        level=Level.INFO,
        format=request.param,
        log_to_console=True,
        log_to_file=True,
        logs_dir=temp_dir
    )


@pytest.fixture(params=[Level.DEBUG, Level.INFO, Level.WARNING, Level.ERROR])
def level_config(request):
    """Параметризованная фикстура для разных уровней"""
    return LogConfig(
        name="level_test_logger",
        level=request.param,
        format=Format.CONSOLE,
        log_to_console=True,
        log_to_file=False
    )


# Хелперы для тестов
def assert_log_contains(capfd, *expected_strings):
    """Проверяет что лог содержит ожидаемые строки"""
    captured = capfd.readouterr()
    output = captured.out + captured.err
    
    for expected in expected_strings:
        assert expected in output, f"Expected '{expected}' not found in log output"


def assert_file_contains(file_path, *expected_strings):
    """Проверяет что файл содержит ожидаемые строки"""
    assert Path(file_path).exists(), f"Log file {file_path} does not exist"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    for expected in expected_strings:
        assert expected in content, f"Expected '{expected}' not found in file {file_path}"


def get_log_file_path(temp_dir, filename="app.log"):
    """Получает путь к файлу логов"""
    return Path(temp_dir) / filename


# Маркеры для категоризации тестов
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow 