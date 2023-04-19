"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from django.urls import re_path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from dotenv import load_dotenv

from app import consumers

load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

asgi_app = get_asgi_application()

# URLs that handle the WebSocket connection are placed here.
websocket_urlpatterns = [
    re_path(r"^ws/chat/(?P<chat_box_name>\w+)/$", consumers.ChatRoomConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        "http": asgi_app,
        "websocket": AuthMiddlewareStack(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
        ),
    }
)
