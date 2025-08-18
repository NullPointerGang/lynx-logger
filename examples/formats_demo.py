"""
Демонстрация различных форматов логирования в LynxLogger
"""

from lynx_logger import setup_logger


def demonstrate_json_format():
    """Демонстрация JSON формата"""
    print("=== JSON Format ===")
    
    logger = setup_logger(
        name="json_demo",
        level="INFO",
        format="json",
        log_to_console=True,
        log_to_file=False
    )
    
    logger.info("JSON format example", user_id=123, action="login", status="success")
    logger.warning("JSON warning", retry_count=3, max_retries=5)
    logger.error("JSON error", error_code="AUTH_FAILED", details="Invalid credentials")


def demonstrate_keyvalue_format():
    """Демонстрация Key-Value формата"""
    print("\n=== Key-Value Format ===")
    
    logger = setup_logger(
        name="keyvalue_demo",
        level="INFO",
        format="keyvalue",
        log_to_console=True,
        log_to_file=False
    )
    
    logger.info("Key-Value format example", user_id=456, action="logout", status="completed")
    logger.warning("Key-Value warning", retry_count=2, max_retries=5)
    logger.error("Key-Value error", error_code="DB_CONNECTION", details="Connection timeout")


def demonstrate_console_format():
    """Демонстрация консольного формата"""
    print("\n=== Console Format ===")
    
    logger = setup_logger(
        name="console_demo",
        level="INFO",
        format="console",
        log_to_console=True,
        log_to_file=False,
        dev_mode=True
    )
    
    logger.info("Console format example", user_id=789, action="profile_update", status="pending")
    logger.warning("Console warning", retry_count=1, max_retries=5)
    logger.error("Console error", error_code="VALIDATION", details="Invalid email format")


def demonstrate_plain_format():
    """Демонстрация простого текстового формата"""
    print("\n=== Plain Format ===")
    
    logger = setup_logger(
        name="plain_demo",
        level="INFO",
        format="plain",
        log_to_console=True,
        log_to_file=False
    )
    
    logger.info("Plain format example", user_id=101, action="password_reset", status="sent")
    logger.warning("Plain warning", retry_count=0, max_retries=5)
    logger.error("Plain error", error_code="RATE_LIMIT", details="Too many requests")


def demonstrate_file_logging():
    """Демонстрация логирования в файл"""
    print("\n=== File Logging ===")
    
    logger = setup_logger(
        name="file_demo",
        level="INFO",
        format="json",
        log_to_console=False,
        log_to_file=True,
        logs_dir="./logs"
    )
    
    logger.info("File logging example", user_id=202, action="data_export", status="processing")
    logger.warning("File warning", retry_count=4, max_retries=5)
    logger.error("File error", error_code="EXPORT_FAILED", details="Disk space insufficient")
    
    print("Логи записаны в файл: ./logs/app.log")


def demonstrate_mixed_logging():
    """Демонстрация смешанного логирования (консоль + файл)"""
    print("\n=== Mixed Logging (Console + File) ===")
    
    logger = setup_logger(
        name="mixed_demo",
        level="INFO",
        format="json",
        log_to_console=True,
        log_to_file=True,
        logs_dir="./logs"
    )
    
    logger.info("Mixed logging example", user_id=303, action="batch_processing", status="started")
    logger.warning("Mixed warning", retry_count=5, max_retries=5)
    logger.error("Mixed error", error_code="BATCH_FAILED", details="Memory limit exceeded")
    
    print("Логи записаны в консоль и файл: ./logs/app.log")


def main():
    """Основная функция демонстрации"""
    print("Демонстрация различных форматов логирования в LynxLogger\n")
    
    demonstrate_json_format()
    demonstrate_keyvalue_format()
    demonstrate_console_format()
    demonstrate_plain_format()
    
    demonstrate_file_logging()
    
    demonstrate_mixed_logging()


if __name__ == "__main__":
    main() 