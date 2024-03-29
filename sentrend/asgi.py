"""
ASGI config for sentrend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


import crawler.routing
from channels.security.websocket import AllowedHostsOriginValidator
from crawler.middleware import TokenAuthMiddleware


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentrend.settings')

# application = ProtocolTypeRouter({
#   "http": get_asgi_application(),
#   "websocket": AuthMiddlewareStack(
#         URLRouter(
#             crawler.routing.websocket_urlpatterns
#         )
#     ),
# })
# application = ProtocolTypeRouter({
#         'websocket': AllowedHostsOriginValidator(
#             TokenAuthMiddleware(
#                 URLRouter(
#                    crawler.routing.websocket_urlpatterns
#                )
#             )
#         )
# })

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
         URLRouter(
            crawler.routing.websocket_urlpatterns
         )
    ),
})