import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Accept the WebSocket connection
        await self.accept()

        # Send a connected message to the client
        await self.send(text_data=json.dumps({'message': 'You are now connected to the chat.'}))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Send a disconnected message to the client
        await self.send(
            text_data=json.dumps({'message': 'You have been disconnected from the chat.'})
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        if text_data:
            try:
                text_data_json = json.loads(text_data)
                message = text_data_json.get('message')  # Use .get() to avoid KeyError
            except json.JSONDecodeError as e:
                # Handle invalid JSON format error
                print(f"Invalid JSON format: {e}")
                return
        else:
            # Handle empty message
            print("Received empty message")
            return

        # Proceed with sending message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {'type': 'chat_message', 'message': message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send the received message back to the client
        await self.send(text_data=json.dumps({'message': message}))
