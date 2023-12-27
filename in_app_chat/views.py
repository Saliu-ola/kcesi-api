from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from .models import InAppChat
from .serializers import InAppChatSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperOrAdminAdmin
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class InAppChatViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = InAppChatSerializer
    permission_classes = [IsSuperOrAdminAdmin]
    queryset = InAppChat.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sender', 'receiver', 'organization', 'group']
    search_fields = ['message']
    ordering_fields = ['created_at']

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="organization",
                description="organization",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
        responses={200: None},
    )
    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-incoming-chats-by-organization',
    )
    def get_total_incoming_chats_by_organization(self, request, pk=None):
        """Get total incoming chats for an organization"""

        organization = request.query_params["organization"]

        output = InAppChat.objects.filter(organization=organization).values('receiver').count()
        if not output:
            return Response(
                {"success": False, "total_chats": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_chats": output},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="organization",
                description="organization",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
        responses={200: None},
    )
    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-outgoing-chats-by-organization',
    )
    def get_total_outgoing_chats_by_organization(self, request, pk=None):
        """Get total outgoing for an organization"""

        organization = request.query_params["organization"]

        output = InAppChat.objects.filter(organization=organization).values('sender').count()
        if not output:
            return Response(
                {"success": False, "total_chats": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_chats": output},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-incoming-chats',
    )
    def get_total_incoming_chats(self, request, pk=None):
        """get total incoming chats in the app"""
        output = InAppChat.objects.filter().values('receiver').count()
        if not output:
            return Response(
                {"success": False, "total_chats": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_chats": output},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-outgoing-chats',
    )
    def get_total_outgoing_chats(self, request, pk=None):
        """get total outgoing in the app"""
        output = InAppChat.objects.filter().values('sender').count()
        if not output:
            return Response(
                {"success": False, "total_chats": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_chats": output},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="group",
                description="group",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
        responses={200},
    )
    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-incoming-chats-by-group',
    )
    def get_total_incoming_chats_by_group(self, request, pk=None):
        """Get total incoming chats by groups"""

        group = request.query_params["group"]
        output = InAppChat.objects.filter(group=group).values('receiver').count()
        if not output:
            return Response(
                {"success": False, "total_chats": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_chats": output},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="group",
                description="group",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
        responses={200},
    )
    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-outgoing-chats-by-group',
    )
    def get_total_outgoing_chats_by_group(self, request, pk=None):
        """Get total outgoing chats by groups"""

        group = request.query_params["group"]
        output = InAppChat.objects.filter(group=group).values('sender').count()
        if not output:
            return Response(
                {"success": False, "total_chats": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_chats": output},
            status=status.HTTP_200_OK,
        )
