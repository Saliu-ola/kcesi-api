from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from organization.models import Organization
from .models import InAppChat
from .serializers import InAppChatSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperAdminOrAdmin
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import django_filters


class InAppChatFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = InAppChat
        fields = [
        'sender',
        'receiver',
        'content_type',
        'organization',
        'group',
        "unique_identifier",
        'start_date',
        'end_date'
        ]


class InAppChatViewSets(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):

    serializer_class = InAppChatSerializer
    permission_classes = [IsAuthenticated]
    queryset = InAppChat.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = [
    #     'sender',
    #     'receiver',
    #     'content_type',
    #     'organization',
    #     'group',
    #     "unique_identifier",
    # ]
    filterset_class = InAppChatFilter 
    search_fields = ['message']
    ordering_fields = ['created_at']

    ADMIN_ROLE_ID = 2
    SUPER_ADMIN_ROLE_ID = 1
    USER_ROLE_ID = 3

    def get_queryset(self):
        if self.request.user.role_id == self.SUPER_ADMIN_ROLE_ID:
            return self.queryset
        elif self.request.user.role_id in [self.ADMIN_ROLE_ID, self.USER_ROLE_ID]:
            organization_id = self.request.user.organization_id
            organization = Organization.objects.filter(organization_id=organization_id).first()
            return self.queryset.filter(organization=organization)

        else:
            raise ValueError("Role id not present")

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
