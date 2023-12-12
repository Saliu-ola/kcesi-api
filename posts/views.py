from accounts.serializers import CurrentUserPostsSerializer
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly,
    IsAdminUser,
)
from rest_framework.request import Request
from rest_framework.response import Response
from .models import Post
from .serializers import PostSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import ReadOnly, AuthorOrReadOnly
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action


class PostViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "put", "post", "delete"]
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Post.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['title', 'author', 'author__organization_id', 'author__group_id']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at']

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)
        return super().perform_create(serializer)

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=["get"],
        detail=False,
        serializer_class=PostSerializer,
        permission_classes=[IsAuthenticated],
        url_path='current_user',
    )
    def get_post_for_current_user(self, request, pk=None):
        current_user_data = Post.objects.filter(author=request.user)
        return self.paginate_results(current_user_data)
