import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "vendor_orders"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # This handles messages sent to the group
    async def order_notification(self, event):
        await self.send(text_data=json.dumps(event["content"]))

    # Receive message from the group
    async def order_alert(self, event):
        message = event['message']
        order_data = event['data']
        
        # Send message to WebSocket (Frontend)
        await self.send(text_data=json.dumps({
            'message': message,
            'data': order_data
        }))