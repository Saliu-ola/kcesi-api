from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from .models import Group, UserGroup
from .serializers import (
    GroupSerializer,
    UserGroupListSerializer,
    UserGroupCreateSerializer,
    UpdateUserGroupSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperAdminOrAdmin
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser


class GroupViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = GroupSerializer
    permission_classes = [AllowAny]
    queryset = Group.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'title',
        'organization_id',
    ]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at']

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserGroupsViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "delete"]
    serializer_class = UserGroupCreateSerializer
    permission_classes = [AllowAny]
    queryset = UserGroup.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'user__organization_name', 'groups']
    ordering_fields = ['created_at']

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return UserGroupListSerializer
        elif self.action == "add":
            return UpdateUserGroupSerializer
        return UserGroupCreateSerializer

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=UpdateUserGroupSerializer,
        url_path='add-group',
    )
    def add(self, request, pk=None):
        serializer = UpdateUserGroupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]
            user_group_instance = get_object_or_404(UserGroup, user=user)
            initial_groups = user_group_instance.groups.all()
            new_groups = serializer.validated_data["groups"]
            user_group_instance.groups.set(list(initial_groups) + list(new_groups))

            return Response(UserGroupCreateSerializer(user_group_instance).data)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=UpdateUserGroupSerializer,
        url_path='remove-group',
    )
    def remove(self, request, pk=None):
        serializer = UpdateUserGroupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]
            user_group_instance = get_object_or_404(UserGroup, user=user)
            groups_to_remove = serializer.validated_data["groups"]
            user_group_instance.groups.remove(*groups_to_remove)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(UserGroupCreateSerializer(user_group_instance).data)
