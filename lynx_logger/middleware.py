"""
Middleware для интеграции с веб-фреймворками
"""

import time
import uuid
from typing import Optional, List
import structlog

from .context import RequestContext, request_id_ctx, user_id_ctx, trace_id_ctx


class FastAPILoggingMiddleware:
    """Middleware для FastAPI с автоматическим логированием запросов"""
    
    def __init__(
        self,
        logger: structlog.BoundLogger,
        log_requests: bool = True,
        log_responses: bool = True,
        exclude_paths: List[str] | None = None,
        include_request_body: bool = False,
        include_response_body: bool = False,
        max_body_size: int = 1024
    ):
        """
        Args:
            logger: Логгер для записи
            log_requests: Логировать входящие запросы
            log_responses: Логировать исходящие ответы  
            exclude_paths: Пути для исключения из логирования
            include_request_body: Включать тело запроса в логи
            include_response_body: Включать тело ответа в логи
            max_body_size: Максимальный размер тела для логирования
        """
        self.logger = logger
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/favicon.ico"]
        self.include_request_body = include_request_body
        self.include_response_body = include_response_body
        self.max_body_size = max_body_size
    
    async def __call__(self, request, call_next):
        """Обработка запроса"""
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
        user_id = request.headers.get("X-User-ID")
        
        if request.url.path in self.exclude_paths:
            response = await call_next(request)
            return response
        
        with RequestContext(request_id=request_id, user_id=user_id, trace_id=trace_id):
            start_time = time.time()

            request_logger = self.logger.bind(
                request_id=request_id,
                trace_id=trace_id,
                user_id=user_id,
                method=request.method,
                path=request.url.path,
                query_params=str(request.query_params) if request.query_params else None,
                user_agent=request.headers.get("User-Agent"),
                client_ip=self._get_client_ip(request)
            )
            
            if self.log_requests:
                log_data = {
                    "event": "Request started",
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": dict(request.query_params),
                    "headers": dict(request.headers)
                }

                if self.include_request_body:
                    body = await self._get_request_body(request)
                    if body:
                        log_data["request_body"] = body
                
                request_logger.info("HTTP request", **log_data)
            
            try:
                response = await call_next(request)
                
                process_time = time.time() - start_time
                
                if self.log_responses:
                    log_data = {
                        "event": "Request completed",
                        "status_code": response.status_code,
                        "process_time": round(process_time, 4),
                        "response_headers": dict(response.headers)
                    }
                    
                    if self.include_response_body:
                        body = await self._get_response_body(response)
                        if body:
                            log_data["response_body"] = body
                    
                    if response.status_code >= 500:
                        request_logger.error("HTTP response", **log_data)
                    elif response.status_code >= 400:
                        request_logger.warning("HTTP response", **log_data)
                    else:
                        request_logger.info("HTTP response", **log_data)
                
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Trace-ID"] = trace_id
                response.headers["X-Process-Time"] = str(round(process_time, 4))
                
                return response
                
            except Exception as exc:
                process_time = time.time() - start_time
                request_logger.exception(
                    "Request failed",
                    exception_type=type(exc).__name__,
                    exception_message=str(exc),
                    process_time=round(process_time, 4)
                )
                raise
    
    def _get_client_ip(self, request) -> str:
        """Получает IP клиента"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return getattr(request.client, "host", "unknown")
    
    async def _get_request_body(self, request) -> Optional[str]:
        """Получает тело запроса для логирования"""
        try:
            body = await request.body()
            if len(body) <= self.max_body_size:
                return body.decode("utf-8", errors="ignore")
            else:
                return f"[Body too large: {len(body)} bytes]"
        except Exception:
            return "[Unable to read body]"
    
    async def _get_response_body(self, response) -> Optional[str]:
        """Получает тело ответа для логирования"""
        # Это сложно реализовать без изменения response
        # Обычно не рекомендуется логировать тело ответа
        return None


class ASGILoggingMiddleware:
    """ASGI middleware для логирования"""
    
    def __init__(
        self,
        app,
        logger: structlog.BoundLogger,
        log_level: str = "INFO"
    ):
        """
        Args:
            app: ASGI приложение
            logger: Логгер
            log_level: Уровень логирования
        """
        self.app = app
        self.logger = logger
        self.log_level = log_level
    
    async def __call__(self, scope, receive, send):
        """ASGI call"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request_id = str(uuid.uuid4())
        
        method = scope["method"]
        path = scope["path"]
        query_string = scope.get("query_string", b"").decode()
        
        start_time = time.time()
        
        request_logger = self.logger.bind(
            request_id=request_id,
            method=method,
            path=path,
            query_string=query_string
        )
        
        request_logger.info("ASGI request started")
        
        async def send_with_logging(message):
            """Wrapper для send с логированием"""
            if message["type"] == "http.response.start":
                status_code = message["status"]
                process_time = time.time() - start_time
                
                request_logger.info(
                    "ASGI request completed",
                    status_code=status_code,
                    process_time=round(process_time, 4)
                )
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_with_logging)
        except Exception as exc:
            process_time = time.time() - start_time
            request_logger.exception(
                "ASGI request failed",
                exception_type=type(exc).__name__,
                exception_message=str(exc),
                process_time=round(process_time, 4)
            )
            raise


class FlaskLoggingMiddleware:
    """Middleware для Flask"""
    
    def __init__(
        self,
        app,
        logger: structlog.BoundLogger,
        log_requests: bool = True,
        log_responses: bool = True
    ):
        """
        Args:
            app: Flask приложение
            logger: Логгер
            log_requests: Логировать запросы
            log_responses: Логировать ответы
        """
        self.app = app
        self.logger = logger
        self.log_requests = log_requests
        self.log_responses = log_responses
        
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_request(self._teardown_request)
    
    def _before_request(self):
        """Обработчик перед запросом"""
        from flask import request, g
        
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        g.request_id = request_id
        g.start_time = time.time()
        
        if self.log_requests:
            request_logger = self.logger.bind(
                request_id=request_id,
                method=request.method,
                path=request.path,
                remote_addr=request.remote_addr
            )
            
            request_logger.info(
                "Flask request started",
                args=dict(request.args),
                form=dict(request.form) if request.form else None
            )
            
            g.request_logger = request_logger
    
    def _after_request(self, response):
        """Обработчик после запроса"""
        from flask import g
        
        if self.log_responses and hasattr(g, 'request_logger'):
            process_time = time.time() - g.start_time
            
            g.request_logger.info(
                "Flask request completed",
                status_code=response.status_code,
                process_time=round(process_time, 4)
            )
        
        if hasattr(g, 'request_id'):
            response.headers["X-Request-ID"] = g.request_id
        
        return response
    
    def _teardown_request(self, exception):
        """Обработчик завершения запроса"""
        from flask import g
        
        if exception and hasattr(g, 'request_logger'):
            process_time = time.time() - g.start_time
            
            g.request_logger.exception(
                "Flask request failed",
                exception_type=type(exception).__name__,
                exception_message=str(exception),
                process_time=round(process_time, 4)
            )


class DjangoLoggingMiddleware:
    """Middleware для Django"""
    
    def __init__(self, get_response):
        """
        Args:
            get_response: Django get_response функция
        """
        self.get_response = get_response
        self.logger = structlog.get_logger("django")
    
    def __call__(self, request):
        """Обработка запроса"""
        request_id = str(uuid.uuid4())
        request.request_id = request_id
        
        start_time = time.time()
        
        request_logger = self.logger.bind(
            request_id=request_id,
            method=request.method,
            path=request.path,
            user=str(request.user) if hasattr(request, 'user') else None
        )
        
        request_logger.info(
            "Django request started",
            query_params=dict(request.GET),
            post_params=dict(request.POST) if request.POST else None
        )
        
        try:
            response = self.get_response(request)
            
            process_time = time.time() - start_time
            request_logger.info(
                "Django request completed",
                status_code=response.status_code,
                process_time=round(process_time, 4)
            )
            
            response["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            process_time = time.time() - start_time
            request_logger.exception(
                "Django request failed",
                exception_type=type(exc).__name__,
                exception_message=str(exc),
                process_time=round(process_time, 4)
            )
            raise 

