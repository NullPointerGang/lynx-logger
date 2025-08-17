# Тесты LynxLogger

Этот каталог содержит комплексные тесты для библиотеки LynxLogger.

## Структура тестов

```
tests/
├── __init__.py              # Пакет тестов
├── conftest.py              # Общие фикстуры и настройки
├── test_core.py             # Тесты основного модуля LynxLogger
├── test_config.py           # Тесты конфигурационного модуля
├── test_setup_logger.py     # Тесты функции setup_logger
├── test_context.py          # Тесты контекстного логирования
├── test_formatters.py       # Тесты форматировщиков
├── test_integration.py      # Интеграционные тесты
└── README.md               # Этот файл
```

## Установка зависимостей для тестирования

```bash
# Базовые зависимости
pip install pytest pytest-cov

# Дополнительные зависимости для расширенного тестирования
pip install pytest-mock pytest-asyncio pytest-xdist
```

## Запуск тестов

### Все тесты
```bash
pytest
```

### Конкретный файл тестов
```bash
pytest tests/test_core.py
```

### Конкретный тест
```bash
pytest tests/test_core.py::TestLynxLogger::test_logger_initialization
```

### Тесты с покрытием кода
```bash
pytest --cov=lynx_logger --cov-report=html --cov-report=term-missing
```

### Параллельный запуск (если установлен pytest-xdist)
```bash
pytest -n auto
```

## Категории тестов

Тесты разделены на категории с помощью маркеров:

### Юнит тесты
```bash
pytest -m unit
```

### Интеграционные тесты
```bash
pytest -m integration
```

### Медленные тесты (пропуск при быстром тестировании)
```bash
pytest -m "not slow"
```

## Описание тестовых модулей

### test_core.py
Тестирует основной класс `LynxLogger`:
- Инициализация логгера
- Консольное и файловое логирование  
- Различные форматы вывода
- Контекстное логирование
- Обработка исключений
- Контекстный менеджер
- Изменение уровня логирования
- Перезагрузка конфигурации

### test_config.py  
Тестирует систему конфигурации:
- Enum'ы Level и Format
- Классы конфигурации (FileConfig, ConsoleConfig и т.д.)
- Создание из словаря и переменных окружения
- Валидация параметров
- Сложные конфигурации

### test_setup_logger.py
Тестирует функцию `setup_logger`:
- Параметры по умолчанию
- Пользовательские параметры
- Обработка ошибок
- Функциональность созданных логгеров
- Производительность

### test_context.py
Тестирует контекстное логирование:
- RequestContext
- ContextProcessor
- ContextLogger
- Вложенные контексты
- Изоляция контекстов

### test_formatters.py
Тестирует форматировщики:
- ConsoleFormatter
- JSONFormatter  
- KeyValueFormatter
- Функция get_formatter
- Обработка ошибок

### test_integration.py
Интеграционные тесты всей системы:
- Комплексные workflow
- Изоляция между логгерами
- Обработка ошибок
- Тесты производительности
- Сценарии реальных приложений

## Фикстуры

В `conftest.py` определены общие фикстуры:

- `temp_dir` - временная директория
- `clean_logging` - очистка logging handlers
- `basic_config/json_config/file_config` - различные конфигурации
- `basic_logger/json_logger/file_logger` - настроенные логгеры
- `sample_log_data` - образцы данных
- Параметризованные фикстуры для форматов и уровней

## Хелперы

Доступны функции-помощники:
- `assert_log_contains()` - проверка содержимого логов
- `assert_file_contains()` - проверка содержимого файлов
- `get_log_file_path()` - получение пути к файлу логов

## Отладка тестов

### Подробный вывод
```bash
pytest -v -s
```

### Остановка на первой ошибке
```bash
pytest -x
```

### Отладка конкретного теста
```bash
pytest tests/test_core.py::TestLynxLogger::test_logger_initialization -v -s --tb=long
```

### Профилирование медленных тестов
```bash
pytest --durations=10
```

## Непрерывная интеграция

Для CI/CD рекомендуется использовать:

```bash
# Быстрые тесты (без медленных)
pytest -m "not slow" --cov=lynx_logger --cov-report=xml

# Полные тесты
pytest --cov=lynx_logger --cov-report=xml --cov-fail-under=85
```

## Добавление новых тестов

При добавлении новых тестов:

1. Создайте тест в соответствующем модуле
2. Используйте описательные имена функций (`test_что_тестируется`)
3. Добавьте docstring с описанием
4. Используйте подходящие фикстуры из `conftest.py`
5. Пометьте тесты соответствующими маркерами
6. Обеспечьте очистку ресурсов (файлы, handlers)

Пример:
```python
@pytest.mark.unit
def test_custom_feature(basic_logger, sample_log_data):
    """Тест пользовательской функции"""
    # Arrange
    logger = basic_logger
    data = sample_log_data
    
    # Act  
    logger.info("Test message", **data)
    
    # Assert
    # Проверки...
```

## Покрытие кода

Цель - минимум 85% покрытия кода. Текущее покрытие можно посмотреть:

```bash
pytest --cov=lynx_logger --cov-report=html
open htmlcov/index.html
```

## Проблемы и решения

### Конфликты handlers
Используйте фикстуру `clean_logging` для очистки между тестами.

### Временные файлы
Используйте фикстуру `temp_dir` для создания временных директорий.

### Долгие тесты
Пометьте медленные тесты маркером `@pytest.mark.slow`.

### Параллельное тестирование
При использовании `-n auto` избегайте глобальных состояний. 