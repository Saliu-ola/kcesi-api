from rest_framework.request import Request
from rest_framework.response import Response
from .models import Resources, Type
from .serializers import ResourcesSerializer, ResourcesTypeSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperOrAdminAdmin
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class ResourcesTypeViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = ResourcesTypeSerializer
    permission_classes = [IsSuperOrAdminAdmin]
    queryset = Type.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'name',
    ]
    search_fields = ['name']
    ordering_fields = ['created_at']

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ResourcesViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = ResourcesSerializer
    permission_classes = [IsSuperOrAdminAdmin]
    queryset = Resources.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'size', 'organization', 'group', 'sender', 'receiver']
    search_fields = ['title']
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
            OpenApiParameter(
                name="type",
                description="Resource type",
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
        url_path='get-total-resources-by-organization',
    )
    def get_total_resources_by_organization(self, request, pk=None):
        """Get total browser_histories for an organization"""

        organization = request.query_params["organization"]
        resource_type = request.query_params["type"]

        output = Resources.objects.filter(organization=organization, type=resource_type).count()
        if not output:
            return Response(
                {"success": False, "total_resources": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_resources": output},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="type",
                description="Resource type",
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
        url_path='get-total-resources',
    )
    def get_total_resources(self, request, pk=None):
        """get total resources in the app"""
        resource_type = request.query_params["type"]

        output = Resources.objects.filter(type=resource_type).count()
        if not output:
            return Response(
                {"success": False, "total_resources": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_resources": output},
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
            OpenApiParameter(
                name="type",
                description="Resource type",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
        
    )
    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-resources-by-group',
    )
    def get_total_resources_by_group(self, request, pk=None):
        """Get total for resources by groups"""
        resource_type = request.query_params["type"]
        group = request.query_params["group"]
        output = Resources.objects.filter(group=group,type=resource_type).count()
        if not output:
            return Response(
                {"success": False, "total_resources": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_resources": output},
            status=status.HTTP_200_OK,
        )
