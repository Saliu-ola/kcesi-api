from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
import time


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        from organization.models import Organization
        from group.models import Group
        from accounts.models import User
        from in_app_chat.models import InAppChat

        if text_data:
            try:
                text_data_json = json.loads(text_data)
                message = text_data_json.get("message")
                sender = text_data_json.get("sender")
                content_type = text_data_json.get("content_type")
                receiver = text_data_json.get("receiver")
                organization_id = text_data_json.get("organization")
                group_id = text_data_json.get("group")
                unique_identifier = text_data_json.get("unique_identifier")
            except json.JSONDecodeError as e:
                print(f"Invalid JSON format: {e}")
                return

            # Use sync_to_async to run synchronous ORM operations
            sender = await sync_to_async(User.objects.get)(pk=sender)
            receiver = await sync_to_async(User.objects.get)(pk=receiver)
            organization = await sync_to_async(Organization.objects.get)(pk=organization_id)

            # Check if group_id is provided, if not, set group to None
            if group_id:
                group = await sync_to_async(Group.objects.get)(pk=group_id)
            else:
                group = None

            created_at = int(time.time())

            # Create and save the InAppChat instance
            chat_message = InAppChat(
                sender=sender,
                content_type=content_type,
                receiver=receiver,
                message=message,
                organization=organization,
                group=group,
                unique_identifier=unique_identifier,
            )
            await sync_to_async(chat_message.save)()

            # Proceed with sending message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    "message": message,
                    "sender": sender.pk,
                    "receiver": receiver.pk,
                    "content_type": content_type,
                    "organization": organization.pk,
                    "group": group.pk if group else None,  # Send None if group is None
                    "unique_identifier": unique_identifier,
                    "created_at": created_at,
                },
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]
        receiver = event["receiver"]
        content_type = event["content_type"]
        organization = event["organization"]
        group = event["group"]  # This will be None if group was not provided
        unique_identifier = event["unique_identifier"]
        created_at = event["created_at"]

        # Send the received message back to the client
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "sender": sender,
                    "content_type": content_type,
                    "receiver": receiver,
                    "organization": organization,
                    "group": group,
                    "unique_identifier": unique_identifier,
                    "created_at": created_at,
                }
            )
        )


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        from organization.models import Organization
        from group.models import Group
        from accounts.models import User
        from forum.models import Forum,ForumComment,CommentReplies

        if text_data:
            try:
                text_data_json = json.loads(text_data)
                forum = text_data_json.get("forum")
                content = text_data_json.get("content")
                organization_id = text_data_json.get("organization")
                group_id = text_data_json.get("group")
                user = text_data_json.get("user")

            except json.JSONDecodeError as e:
                print(f"Invalid JSON format: {e}")
                return

            # Use sync_to_async to run synchronous ORM operations
            forum = await sync_to_async(Forum.objects.get)(pk=user)
            user = await sync_to_async(User.objects.get)(pk=user)
            organization = await sync_to_async(Organization.objects.get)(pk=organization_id)
            group = await sync_to_async(Group.objects.get)(pk=group_id)

            created_at = int(time.time())

            # Create and save the InAppChat instance
            comment = ForumComment(
                forum=forum,
                content=content,
                organization=organization,
                group=group,
                user=user,
            )
            await sync_to_async(comment.save)()

            # Proceed with sending message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'comment',
                    "forum": forum.pk,
                    "content": content,
                    "organization": organization.pk,
                    "group": group.pk,
                    "user":user.pk,
                    "created_at": created_at,
                },
            )

    # Receive message from room group
    async def comment(self, event):
        forum = event["forum"]
        content = event["content"]
        organization = event["organization"]
        group = event["group"]
        user = event["user"]
        created_at = event["created_at"]

        # Send the received message back to the client
        await self.send(
            text_data=json.dumps(
                {
                    "forum": forum,
                    "content": content,
                    "organization": organization,
                    "group": group,
                    "user": user,
                }
            )
        )


class RepliesConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        from organization.models import Organization
        from group.models import Group
        from accounts.models import User
        from forum.models import Forum, ForumComment, CommentReplies

        if text_data:
            try:
                text_data_json = json.loads(text_data)
                forum = text_data_json.get("forum")
                content = text_data_json.get("content")
                organization_id = text_data_json.get("organization")
                group_id = text_data_json.get("group")
                user = text_data_json.get("user")

            except json.JSONDecodeError as e:
                print(f"Invalid JSON format: {e}")
                return

            # Use sync_to_async to run synchronous ORM operations
            comment = await sync_to_async(comment.objects.get)(pk=user)
            user = await sync_to_async(User.objects.get)(pk=user)
            organization = await sync_to_async(Organization.objects.get)(pk=organization_id)
            group = await sync_to_async(Group.objects.get)(pk=group_id)

            created_at = int(time.time())

            # Create and save the InAppChat instance
            reply = CommentReplies(
                comment=comment,
                content=content,
                organization=organization,
                group=group,
                user=user,
            )
            await sync_to_async(reply.save)()

            # Proceed with sending message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'reply',
                    "comment": comment.pk,
                    "content": content,
                    "organization": organization.pk,
                    "group": group.pk,
                    "user": user.pk,
                    "created_at": created_at,
                },
            )

    # Receive message from room group
    async def reply(self, event):
        comment = event["comment"]
        content = event["content"]
        organization = event["organization"]
        group = event["group"]
        user = event["user"]
        created_at = event["created_at"]

        # Send the received message back to the client
        await self.send(
            text_data=json.dumps(
                {
                    "comment": comment,
                    "content": content,
                    "organization": organization,
                    "group": group,
                    "user": user,
                }
            )
        )
