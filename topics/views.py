from rest_framework.request import Request
from rest_framework.response import Response
from .models import Topic
from .serializers import TopicSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperOrAdminAdmin
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class TopicViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = TopicSerializer
    permission_classes = [IsSuperOrAdminAdmin]
    queryset = Topic.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'author', 'platform', 'organization', 'group']
    search_fields = ['name']
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
        url_path='get-total-topics-by-organization',
    )
    def get_total_topics_by_organization(self, request, pk=None):
        """Get total topics for an organization"""

        organization = request.query_params["organization"]

        output = Topic.objects.filter(organization=organization).count()
        if not output:
            return Response(
                {"success": False, "total_topics": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_topics": output},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-topics',
    )
    def get_total_topics(self, request, pk=None):
        """get total topics in the app"""
        output = Topic.objects.count()
        if not output:
            return Response(
                {"success": False, "total_topics": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_topics": output},
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
        url_path='get-total-topics-by-group',
    )
    def get_total_topics_by_group(self, request, pk=None):
        """Get total for an  organization topics by groups"""

        group = request.query_params["group"]
        output = Topic.objects.filter(group=group).count()
        if not output:
            return Response(
                {"success": False, "total_topics": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_topics": output},
            status=status.HTTP_200_OK,
        )
