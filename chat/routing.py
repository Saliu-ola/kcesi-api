# chat/routing.py
from django.urls import re_path

from chat.consumers import (
    ChatConsumer,
    CommentConsumer,
    RepliesConsumer,
    BlogCommentConsumer,
    BlogCommentRepliesConsumer,
)

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'^ws/forums/comments/(?P<room_name>\w+)/$', CommentConsumer.as_asgi()),
    re_path(r'^ws/forums/comment-replies/(?P<room_name>\w+)/$', RepliesConsumer.as_asgi()),
    re_path(r'^ws/blogs/comments/(?P<room_name>\w+)/$', BlogCommentConsumer.as_asgi()),
    re_path(r'^ws/blogs/comment-replies/(?P<room_name>\w+)/$', BlogCommentRepliesConsumer.as_asgi()),
]
