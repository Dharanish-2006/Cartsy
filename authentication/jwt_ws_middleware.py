from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except:
        return None

class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query = parse_qs(scope["query_string"].decode())
        token = query.get("token", [None])[0]

        scope["user"] = None

        if token:
            try:
                access = AccessToken(token)
                user = await get_user(access["user_id"])
                scope["user"] = user
            except Exception as e:
                print("JWT ERROR:", e)

        return await self.app(scope, receive, send)