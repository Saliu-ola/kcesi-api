from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json


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
        from organization.models import Organization
        from group.models import Group
        from accounts.models import User
        from in_app_chat.models import InAppChat
        #decided to import the apps in the function to avoid app registry
        
        if text_data:
            try:
                text_data_json = json.loads(text_data)
                message = text_data_json.get('message')
                sender_id = text_data_json.get('sender_id')
                receiver_id = text_data_json.get('receiver_id')
                organization = text_data_json.get('organization')
                group = text_data_json.get('group')
            except json.JSONDecodeError as e:
                print(f"Invalid JSON format: {e}")
                return
            
            # Use sync_to_async to run synchronous ORM operations
        
            
            sender = await sync_to_async(User.objects.get)(pk=sender_id)
            receiver = await sync_to_async(User.objects.get)(pk=receiver_id)
            organization = await sync_to_async(Organization.objects.get)(pk=organization)
            group = await sync_to_async(Group.objects.get)(pk=group)

            # Create and save the InAppChat instance
            chat_message = InAppChat(
                sender=sender,
                receiver=receiver,
                message=message,
                organization=organization,
                group=group,
            )
            await sync_to_async(chat_message.save)()

            # Proceed with sending message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {'type': 'chat_message', 'message': message}
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send the received message back to the client
        await self.send(text_data=json.dumps({'message': message}))
