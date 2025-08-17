"""
Интеграционные тесты для LynxLogger
"""

import pytest
import json
import os
import logging
import tempfile
import shutil
from pathlib import Path
import time

from lynx_logger import setup_logger, LynxLogger, LogConfig, Level, Format
from lynx_logger.config import FileConfig, ConsoleConfig, ContextConfig
from lynx_logger.context import RequestContext, ContextLogger


@pytest.mark.integration
class TestEndToEndLogging:
    """Комплексные end-to-end тесты"""
    
    def setup_method(self):
        """Подготовка к каждому тесту"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Очистка после каждого теста"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
    def test_complete_logging_workflow(self):
        """Тест полного рабочего процесса логирования"""
        logger = setup_logger(
            name="workflow_test",
            level="DEBUG",
            format="json",
            dev_mode=True,
            log_to_console=True,
            log_to_file=True,
            logs_dir=self.temp_dir
        )
        
        logger.debug("Debug message", component="auth", action="validate")
        logger.info("User login", user_id=123, session_id="sess_456")
        logger.warning("Rate limit warning", user_id=123, attempts=5)
        logger.error("Database connection failed", error="timeout", retry_count=3)

        bound_logger = logger.bind(request_id="req_789", trace_id="trace_abc")
        bound_logger.info("Processing request", endpoint="/api/users")
        
        try:
            raise ValueError("Test exception for integration test")
        except ValueError:
            logger.exception("Exception occurred during processing")
        
        log_file = Path(self.temp_dir) / "app.log"
        assert log_file.exists()
        
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        assert "Debug message" in log_content
        assert "User login" in log_content
        assert "Rate limit warning" in log_content
        assert "Database connection failed" in log_content
        assert "Processing request" in log_content
        assert "Exception occurred during processing" in log_content
        
        lines = [line for line in log_content.strip().split('\n') if line]
        for line in lines:
            try:
                json.loads(line)
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON line: {line}")
                
    def test_multi_logger_isolation(self):
        """Тест изоляции между несколькими логгерами"""
        auth_logger = setup_logger(
            name="auth_service",
            level="INFO",
            format="json",
            log_to_file=True,
            logs_dir=self.temp_dir,
            file=FileConfig(filename="auth.log")
        )
        
        payment_logger = setup_logger(
            name="payment_service", 
            level="DEBUG",
            format="keyvalue",
            log_to_file=True,
            logs_dir=self.temp_dir,
            file=FileConfig(filename="payment.log")
        )
        
        auth_logger.info("User authenticated", user_id=123)
        payment_logger.debug("Payment initiated", amount=99.99, currency="USD")
        
        for handler in logging.getLogger().handlers:
            handler.flush()
        
        auth_log = Path(self.temp_dir) / "auth.log" 
        payment_log = Path(self.temp_dir) / "payment.log"
        
        assert auth_log.exists()
        assert payment_log.exists()
        
        with open(auth_log, 'r') as f:
            auth_content = f.read()
        with open(payment_log, 'r') as f:
            payment_content = f.read()
            
        assert "User authenticated" in auth_content
        assert "user_id" in auth_content
        assert "Payment initiated" not in auth_content
        
        assert "Payment initiated" in payment_content
        assert "amount=99.99" in payment_content
        assert "User authenticated" not in payment_content
        
    def test_context_propagation_workflow(self, capfd):
        """Тест распространения контекста через весь workflow"""
        logger = setup_logger(
            name="context_workflow",
            level="INFO",
            format="console",
            log_to_console=True,
            log_to_file=False
        )
        
        with RequestContext(request_id="req_12345", user_id="user_67890"):
            logger.info("Request received", method="POST", path="/api/orders")
            
            order_logger = logger.bind(order_id="order_999", total_amount=150.00)
            order_logger.info("Order validation started")
            
            with RequestContext(trace_id="trace_external_call"):
                order_logger.info("Calling payment service")
                order_logger.info("Payment processed successfully")
                
            order_logger.info("Order created successfully")
            
        logger.info("Request completed")
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert "Request received" in output
        assert "Order validation started" in output
        assert "Calling payment service" in output
        assert "Payment processed successfully" in output
        assert "Order created successfully" in output
        assert "Request completed" in output
        
    def test_error_handling_and_recovery(self):
        """Тест обработки ошибок и восстановления"""
        logger = setup_logger(
            name="error_handling_test",
            level="INFO",
            format="json",
            log_to_console=False,
            log_to_file=True,
            logs_dir=self.temp_dir
        )
        
        logger.info("Starting error handling test")
        
        try:
            open("/nonexistent/path/file.txt", 'r')
        except FileNotFoundError as e:
            logger.error("File system error", error_type="FileNotFoundError", path="/nonexistent/path/file.txt")
        
        try:
            raise ValueError("Invalid user input")
        except ValueError as e:
            logger.exception("User input validation failed", input_value="invalid_data")
        
        logger.warning("Network timeout", service="external_api", timeout_seconds=30, retry_count=2)
        
        logger.info("Error handling completed, service recovered")
        
        log_file = Path(self.temp_dir) / "app.log"
        assert log_file.exists()
        
        with open(log_file, 'r') as f:
            log_lines = f.readlines()
            
        assert len(log_lines) >= 4
        
        for line in log_lines:
            if line.strip():
                data = json.loads(line)
                assert "timestamp" in data
                assert "level" in data
                assert "event" in data
                
    def test_performance_under_load(self):
        """Тест производительности под нагрузкой"""
        logger = setup_logger(
            name="performance_test",
            level="INFO", 
            format="json",
            log_to_console=False,
            log_to_file=True,
            logs_dir=self.temp_dir
        )
        
        start_time = time.time()
        
        message_count = 1000
        for i in range(message_count):
            logger.info(
                f"Performance test message {i}",
                iteration=i,
                batch=i // 100,
                test_data=f"data_{i}"
            )
            
        end_time = time.time()
        duration = end_time - start_time
        
        for handler in logging.getLogger().handlers:
            handler.flush()
            
        log_file = Path(self.temp_dir) / "app.log"
        assert log_file.exists()
        
        with open(log_file, 'r') as f:
            log_lines = f.readlines()
            
        assert len(log_lines) >= message_count
        
        messages_per_second = message_count / duration
        assert messages_per_second > 100, f"Too slow: {messages_per_second} messages/sec"
        
        logger.info("Performance test completed", 
                   duration_seconds=duration,
                   messages_per_second=messages_per_second)
                   
    def test_configuration_flexibility(self):
        """Тест гибкости конфигурации"""
        config = LogConfig(
            name="flexible_logger",
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
                filename="flexible.log",
                max_size="1MB",
                backup_count=3,
                encoding="utf-8"
            ),
            context=ContextConfig(
                include_caller=True,
                include_thread=True,
                custom_fields={"service": "test_service", "version": "1.0.0"}
            ),
            timestamp_format="iso",
            structured_logging=True
        )
        
        logger = LynxLogger(config)
        
        assert logger.config.name == "flexible_logger"
        assert logger.config.level == Level.DEBUG
        assert logger.config.format == Format.JSON
        assert logger.config.dev_mode is True
        assert logger.config.console.show_thread is True
        assert logger.config.file.max_size == "1MB"
        assert logger.config.context.include_caller is True
        assert logger.config.context.custom_fields["service"] == "test_service"
        
        logger.debug("Flexible configuration test", feature="advanced_config")
        
        log_file = Path(self.temp_dir) / "flexible.log"
        assert log_file.exists()
        
    def test_real_world_application_scenario(self, capfd):
        """Тест сценария реального приложения"""
        api_logger = setup_logger(
            name="api_gateway",
            level="INFO",
            format="json",
            log_to_console=True,
            log_to_file=True,
            logs_dir=self.temp_dir,
            file=FileConfig(filename="api_gateway.log")
        )
        
        auth_logger = setup_logger(
            name="auth_service",
            level="DEBUG", 
            format="json",
            log_to_console=False,
            log_to_file=True,
            logs_dir=self.temp_dir,
            file=FileConfig(filename="auth_service.log")
        )
        
        request_id = "req_real_world_123"
        user_id = "user_456"
        
        with RequestContext(request_id=request_id):
            api_logger.info("Incoming request", 
                          method="POST", 
                          path="/api/v1/users/login",
                          ip="192.168.1.100",
                          user_agent="Mozilla/5.0")
            
            with RequestContext(user_id=user_id):
                auth_logger.debug("Authentication request received")
                auth_logger.info("Validating credentials")
                
                db_logger = auth_logger.bind(query="SELECT * FROM users", table="users")
                db_logger.debug("Database query executed", duration_ms=45)
                
                auth_logger.info("Authentication successful", login_method="password")
                
            api_logger.info("Request processed successfully",
                          status_code=200,
                          response_time_ms=150)
                          
        captured = capfd.readouterr()
        
        assert "Incoming request" in captured.out
        assert "Request processed successfully" in captured.out
        
        api_log = Path(self.temp_dir) / "api_gateway.log"
        auth_log = Path(self.temp_dir) / "auth_service.log"
        
        assert api_log.exists()
        assert auth_log.exists()
        
        with open(api_log, 'r') as f:
            api_content = f.read()
            
        assert "Incoming request" in api_content
        assert "POST" in api_content
        assert "/api/v1/users/login" in api_content
        assert "Request processed successfully" in api_content
        
        with open(auth_log, 'r') as f:
            auth_content = f.read()
            
        assert "Authentication request received" in auth_content
        assert "Validating credentials" in auth_content
        assert "Database query executed" in auth_content
        assert "Authentication successful" in auth_content 

