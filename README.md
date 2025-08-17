# LynxLogger

Универсальная библиотека структурированного логирования на основе `structlog` с расширенными возможностями для Python приложений.

## Особенности
- **Простая настройка** - от одной строки кода до детальной конфигурации
- **Структурированное логирование** с поддержкой JSON, Key-Value и консольных форматов
- **Контекстное логирование** с автоматической трассировкой запросов
- **Фильтрация** по уровню, источнику, содержимому сообщений
- **Ротация файлов** с настраиваемыми параметрами
- **Middleware** для FastAPI, Flask, Django и ASGI приложений
- **Обратная совместимость** с вашим текущим кодом

## Установка

```bash
pip install lynx-logger
```

Дополнительные пакеты для веб-фреймворков:
```bash
pip install lynx-logger[web]  # FastAPI, Flask, Django
pip install lynx-logger[all]  # Все зависимости + dev tools
```

## Быстрый старт

### Базовое использование

```python
from lynx_logger import setup_logger

logger = setup_logger("my_app")
logger.info("Application started", version="1.0.0")

logger = setup_logger(
    name="my_app",
    level="DEBUG", 
    format="json",
    log_to_file=True,
    logs_dir="./logs"
)

logger.info("User logged in", user_id=123, ip="192.168.1.1")
```

### Продвинутая настройка

```python
from lynx_logger import LynxLogger, LogConfig, Level, Format

config = LogConfig(
    name="my_app",
    level=Level.DEBUG,
    format=Format.JSON,
    dev_mode=True,
    log_to_console=True,
    log_to_file=True,
    logs_dir="./logs"
)

logger = LynxLogger(config)
logger.info("Application configured", config=config.to_dict())
```

## Интеграция с веб-фреймворками

### FastAPI

```python
from fastapi import FastAPI
from lynx_logger import setup_logger, FastAPILoggingMiddleware

app = FastAPI()
logger = setup_logger("fastapi_app", format="json")

# Добавляем middleware
app.add_middleware(FastAPILoggingMiddleware, logger=logger.get_logger())

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Hello World"}
```

### Flask

```python
from flask import Flask
from lynx_logger import setup_logger, FlaskLoggingMiddleware

app = Flask(__name__)
logger = setup_logger("flask_app")

# Добавляем middleware
FlaskLoggingMiddleware(app, logger.get_logger())

@app.route("/")
def hello():
    logger.info("Hello endpoint called")
    return "Hello World"
```

### Django (в settings.py)

```python
# settings.py
MIDDLEWARE = [
    'lynx_logger.middleware.DjangoLoggingMiddleware',
    # ... другие middleware
]
```

## Форматы вывода

### Console (цветной вывод для разработки)
```python
logger = setup_logger("app", format="console", dev_mode=True)
logger.info("Server started", port=8000)
# 2025-01-16T10:30:45 [INFO] app: Server started port=8000
```

### JSON (для продакшна)
```python  
logger = setup_logger("app", format="json")
logger.info("User action", user_id=123, action="login")
# {"timestamp": "2025-01-16T10:30:45", "level": "info", "logger": "app", "event": "User action", "user_id": 123, "action": "login"}
```

### Key-Value
```python
logger = setup_logger("app", format="keyvalue")
logger.info("Payment processed", amount=100, currency="USD")
# timestamp=2025-01-16T10:30:45 level=info logger=app event='Payment processed' amount=100 currency=USD
```

## Контекстное логирование

### Автоматический контекст

```python
from lynx_logger import RequestContext

with RequestContext(request_id="req_123", user_id="user_456"):
    logger.info("Processing request")
    # Автоматически добавит request_id и user_id во все логи
```

### Привязка контекста

```python
# Создаем логгер с постоянным контекстом
user_logger = logger.bind(user_id=123, session_id="sess_456")
user_logger.info("User performed action", action="purchase")

# Временный контекст
with logger.with_context(trace_id="trace_789"):
    logger.info("Processing trace")
```

### Стековый контекст

```python
from lynx_logger import ContextLogger

context_logger = ContextLogger(logger.get_logger())

# Добавляем контекст в стек
request_logger = context_logger.with_request("req_123", "user_456")
request_logger.info("Request started")

# Добавляем еще контекст
operation_logger = request_logger.with_trace("trace_789")
operation_logger.info("Operation completed")
```

## Фильтрация логов

### Встроенные фильтры

```python
from lynx_logger import LogConfig, FilterConfig, Level

config = LogConfig(
    name="app",
    filters=FilterConfig(
        min_level=Level.WARNING,  # Только WARNING и выше
        exclude_loggers=["urllib3", "requests"],  # Исключаем библиотеки
        exclude_messages=["health.*", "ping"]  # Исключаем по regex
    )
)

logger = LynxLogger(config)
```

### Пользовательские фильтры

```python
from lynx_logger import SourceFilter, ContentFilter

# Фильтр по исходному файлу
source_filter = SourceFilter(
    include_patterns=["my_app.*"],
    exclude_patterns=["test_.*"]
)

# Фильтр по содержимому
content_filter = ContentFilter(
    exclude_patterns=["password", "secret"],
    case_sensitive=False
)
```

## Конфигурация

### Из переменных окружения

```bash
export LOG_NAME=my_app
export LOG_LEVEL=DEBUG
export LOG_FORMAT=json
export LOG_TO_FILE=true
export LOG_LOGS_DIR=/var/log/my_app
```

```python
from lynx_logger import LogConfig

config = LogConfig.from_env()
logger = LynxLogger(config)
```

### Из словаря

```python
config_dict = {
    "name": "my_app",
    "level": "INFO",
    "format": "json",
    "log_to_file": True,
    "file": {
        "filename": "app.log",
        "max_size": "50MB",
        "backup_count": 10
    }
}

config = LogConfig.from_dict(config_dict)
logger = LynxLogger(config)
```

## Продвинутые возможности

### Ротация файлов

```python
from lynx_logger import LogConfig, FileConfig

config = LogConfig(
    name="app",
    log_to_file=True,
    file=FileConfig(
        filename="app.log",
        max_size="10MB",      # Максимальный размер файла
        backup_count=5,       # Количество архивных файлов
        encoding="utf-8"
    )
)
```

### Throttling (ограничение частоты)

```python
from lynx_logger import ThrottleFilter

# Не более 10 одинаковых сообщений в минуту
throttle = ThrottleFilter(max_repeats=10, time_window=60)
```

### Пользовательские процессоры

```python
def add_hostname(logger, name, event_dict):
    import socket
    event_dict["hostname"] = socket.gethostname()
    return event_dict

config = LogConfig(
    name="app",
    extra_processors=[add_hostname]
)
```

## Примеры использования

### Микросервис с трассировкой

```python
from fastapi import FastAPI, Request
from lynx_logger import setup_logger, RequestContext
import uuid

app = FastAPI()
logger = setup_logger("payment_service", format="json")

@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    with RequestContext(request_id=request_id):
        logger.info("Request started", path=request.url.path)
        response = await call_next(request)
        logger.info("Request completed", status=response.status_code)
        return response

@app.post("/pay")
async def process_payment(amount: float, currency: str):
    payment_logger = logger.bind(amount=amount, currency=currency)
    payment_logger.info("Payment processing started")
    
    # Бизнес-логика
    result = {"status": "success", "transaction_id": str(uuid.uuid4())}
    
    payment_logger.info("Payment completed", result=result)
    return result
```

### Обработка ошибок

```python
from lynx_logger import setup_logger

logger = setup_logger("error_handler", format="json")

def process_user_data(user_id: int, data: dict):
    user_logger = logger.bind(user_id=user_id)
    
    try:
        user_logger.info("Processing user data", data_keys=list(data.keys()))
        
        # Бизнес-логика
        if not data.get("email"):
            raise ValueError("Email is required")
        
        user_logger.info("User data processed successfully")
        return {"status": "success"}
        
    except ValueError as e:
        user_logger.warning("Validation error", error=str(e))
        return {"status": "error", "message": str(e)}
        
    except Exception as e:
        user_logger.exception("Unexpected error occurred")
        return {"status": "error", "message": "Internal error"}
```

## Лицензия

MIT License - используйте свободно в коммерческих и некоммерческих проектах.

## Поддержка

- **GitHub Issues**: [Сообщить о проблеме](https://github.com/NullPointerGang/lynx-logger/issues)
- **Email**: flacsy.x@gmail.gom
