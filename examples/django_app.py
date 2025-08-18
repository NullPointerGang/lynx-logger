"""
Пример Django приложения с LynxLogger
"""

import django
from django.conf import settings
from django.http import JsonResponse
from django.urls import path
from django.core.wsgi import get_wsgi_application
from django.views.decorators.csrf import csrf_exempt
from lynx_logger import LynxLogger, Level, Format
from lynx_logger.config import LogConfig, FileConfig


if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='django-lynx-logger-example',
        ROOT_URLCONF=__name__,
        MIDDLEWARE=[
            'lynx_logger.middleware.DjangoLoggingMiddleware',
        ],
    )
    django.setup()

logger = LynxLogger(
    LogConfig(
        name="django_app", 
        level=Level.INFO, 
        format=Format.JSON, 
        log_to_console=True, 
        file=FileConfig(
            enabled=True,
            filename="django_app.log",
            max_size="10MB",
            backup_count=5,
            delay=True
        )
    )
)

@csrf_exempt
def home_view(request):
    """Главная страница"""
    logger.info("Django request received", path=request.path, method=request.method)
    
    logger.debug("Processing request data", user_agent=request.META.get('HTTP_USER_AGENT'))
    
    return JsonResponse({"message": "Hello from Django!", "framework": "Django"})


@csrf_exempt
def api_view(request):
    """API endpoint"""
    logger.info("API request received", path=request.path, method=request.method)
    
    data = request.GET.dict() if request.method == 'GET' else request.POST.dict()
    logger.info("Request data", data=data)
    
    return JsonResponse({
        "status": "success",
        "data": data,
        "message": "API endpoint working"
    })

urlpatterns = [
    path('', home_view, name='home'),
    path('api/', api_view, name='api'),
]

application = get_wsgi_application()


if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000']) 