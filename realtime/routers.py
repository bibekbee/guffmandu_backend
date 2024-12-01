from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("connection-request/", consumers.ConnectionConsumer.as_asgi()),
]