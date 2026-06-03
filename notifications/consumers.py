import json
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = await self.get_user_from_token()

        if not self.user or self.user.is_anonymous:
            await self.close()
            return

        self.group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "Notification WebSocket connected."
        }))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def get_user_from_token(self):
        query_string = self.scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)

        token_key = None

        if "token" in query_params:
            token_key = query_params["token"][0]

        if not token_key:
            return AnonymousUser()

        return await self.get_user(token_key)

    @database_sync_to_async
    def get_user(self, token_key):
        try:
            token = Token.objects.select_related("user").get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return AnonymousUser()