import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AdminNotificationConsumer(AsyncWebsocketConsumer):
    GROUP = "admin_notifications"

    async def connect(self):
        # Require authenticated staff user
        user = self.scope.get("user")
        if not user or not user.is_staff:
            await self.close()
            return

        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)

    # Handler: called by group_send with type="new_order"
    async def new_order(self, event):
        await self.send(text_data=json.dumps({
            "type": "new_order",
            "order_id": event["order_id"],
            "amount": event["amount"],
            "customer": event["customer"],
        }))