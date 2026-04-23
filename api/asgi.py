import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()
from OrderManagement.middleware import JWTAuthMiddleware
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
})