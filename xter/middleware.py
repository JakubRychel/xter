from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication

@database_sync_to_async
def get_user(token):
    jwt_auth = JWTAuthentication()
    try:
        validated_token = jwt_auth.get_validated_token(token)
        return jwt_auth.get_user(validated_token)
    except:
        return AnonymousUser()
    
class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        token = None

        proto = headers.get(b'sec-websocket-protocol')

        if proto:
            proto = proto.decode()

            if ',' in proto:
                token = proto.split(',', 1)[1]
            else:
                token = proto

        if not token:
            query = parse_qs(scope['query_string'].decode())
            token = query.get('token', [None])[0]

        if token:
            scope['user'] = await get_user(token)
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)