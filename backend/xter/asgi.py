import os
import django
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xter.settings')

django_asgi_app = get_asgi_application()
static_handler = ASGIStaticFilesHandler(django_asgi_app)

from xter.middleware import JWTAuthMiddleware
import notifications.routing

application = ProtocolTypeRouter({
    'http': static_handler,
    'websocket': JWTAuthMiddleware(
        URLRouter(
            notifications.routing.websocket_urlpatterns
        )
    ),
})
