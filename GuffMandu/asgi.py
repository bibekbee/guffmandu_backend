import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from realtime.routers import websocket_urlpatterns

settings_module = 'GuffMandu.deployment_settings' if 'RENDER_EXTERNAL_HOSTNAME' in os.environ else 'GuffMandu.settings'

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,

    # WebSocket chat handler
    "websocket": 
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),

    # This is commented out because we wanna allow anyone for now in development process
    # "websocket": AllowedHostsOriginValidator(
    #     AuthMiddlewareStack(
    #         URLRouter(websocket_urlpatterns)
    #     )
    # ),
})