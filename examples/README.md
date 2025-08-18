# Примеры использования LynxLogger

Этот каталог содержит примеры использования LynxLogger в различных сценариях.

## Доступные примеры

### 1. [simple_app.py](simple_app.py) - Простой пример
Базовый пример использования LynxLogger без веб-фреймворка.

**Особенности:**
- Создание логгера с помощью `setup_logger`
- Логирование с контекстом (`RequestContext`)
- Обработка исключений
- Логирование в файл и консоль

**Запуск:**
```bash
python3 simple_app.py
```

### 2. [formats_demo.py](formats_demo.py) - Демонстрация форматов
Показывает различные форматы логирования.

**Особенности:**
- JSON формат
- Key-Value формат
- Консольный формат (с цветами)
- Простой текстовый формат
- Логирование в файл
- Смешанное логирование (консоль + файл)

**Запуск:**
```bash
python3 formats_demo.py
```

### 3. [fastapi_app.py](fastapi_app.py) - FastAPI приложение
Пример интеграции с FastAPI.

**Особенности:**
- FastAPI приложение с middleware
- Автоматическое логирование HTTP запросов
- Контекстная информация (request_id, trace_id)
- Логирование времени обработки

**Запуск:**
```bash
# Требует установки FastAPI и uvicorn
pip install fastapi uvicorn
python3 fastapi_app.py
```

### 4. [flask_app.py](flask_app.py) - Flask приложение
Пример интеграции с Flask.

**Особенности:**
- Flask приложение с middleware
- Автоматическое логирование запросов
- Логирование параметров запроса

**Запуск:**
```bash
# Требует установки Flask
pip install flask
python3 flask_app.py
```

### 5. [django_app.py](django_app.py) - Django приложение
Пример интеграции с Django.

**Особенности:**
- Django приложение с middleware
- Автоматическое логирование запросов
- Логирование данных запроса
- Использование `LynxLogger` напрямую

**Запуск:**
```bash
# Требует установки Django
pip install django
python3 django_app.py
```

## Структура логов

Все примеры создают логи в директории `./logs/`:

- `app.log` - основной файл логов
- `fastapi_app.log` - логи FastAPI приложения
- `flask_app.log` - логи Flask приложения
- `django_app.log` - логи Django приложения

## Форматы логов

LynxLogger поддерживает следующие форматы:

1. **JSON** - структурированный JSON формат
2. **Key-Value** - формат ключ=значение
3. **Console** - цветной консольный формат
4. **Plain** - простой текстовый формат

## Контекстное логирование

Примеры демонстрируют использование `RequestContext` для автоматического добавления контекстной информации:

```python
with RequestContext(request_id="req_123", user_id="user_456"):
    logger.info("Обработка запроса")
```

## Привязанные логгеры

Примеры показывают создание привязанных логгеров с дополнительными полями:

```python
api_logger = logger.bind(component="api", version="v1")
user_logger = api_logger.bind(user_id="user_789")
```

## Создание логгера

Примеры демонстрируют два способа создания логгера:

### 1. Через `setup_logger` (простой способ)
```python
from lynx_logger import setup_logger

logger = setup_logger(
    name="my_app",
    level="INFO",
    format="json",
    log_to_console=True,
    log_to_file=True,
    logs_dir="./logs"
)
```

### 2. Через `LynxLogger` напрямую (продвинутый способ)
```python
from lynx_logger import LynxLogger, Level, Format
from lynx_logger.config import LogConfig, FileConfig

logger = LynxLogger(
    LogConfig(
        name="my_app",
        level=Level.INFO,
        format=Format.JSON,
        log_to_console=True,
        file=FileConfig(
            enabled=True,
            filename="my_app.log",
            max_size="10MB",
            backup_count=5
        )
    )
)
```

## Запуск примеров

Для запуска примеров без веб-фреймворков:

```bash
python3 simple_app.py
python3 formats_demo.py
```

Для запуска примеров с веб-фреймворками требуется установка соответствующих зависимостей. 
