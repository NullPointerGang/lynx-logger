"""
Простой пример использования LynxLogger без веб-фреймворка
"""

from lynx_logger import setup_logger
from lynx_logger.context import RequestContext


def main():
    logger = setup_logger(
        name="simple_app",
        level="INFO",
        format="json",
        log_to_console=True,
        log_to_file=True,
        logs_dir="./logs"
    )
    
    logger.info("Приложение запущено", version="1.0.0")
    
    with RequestContext(request_id="req_123", user_id="user_456"):
        logger.info("Обработка запроса", endpoint="/api/data")
        
        logger.debug("Получение данных из базы", table="users")
        
        try:
            result = 10 / 0
        except ZeroDivisionError:
            logger.error("Ошибка при обработке данных", error="division_by_zero")
        
        logger.info("Запрос обработан", status="completed")
    
    logger.info("Приложение завершено")


if __name__ == "__main__":
    main() 