from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from .models import BrowserHistory
from .serializers import BrowserHistorySerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperOrAdminAdmin
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class BrowserHistoryViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = BrowserHistorySerializer
    permission_classes = [IsSuperOrAdminAdmin]
    queryset = BrowserHistory.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'organization', 'group', 'start_time', 'end_time']
    search_fields = ['url']
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
        url_path='get-total-browser-histories-by-organization',
    )
    def get_total_browser_histories_by_organization(self, request, pk=None):
        """Get total browser_histories for an organization"""

        organization = request.query_params["organization"]

        output = BrowserHistory.objects.filter(organization=organization).count()
        if not output:
            return Response(
                {"success": False, "total_browser_histories": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_browser_histories": output},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-browser-histories',
    )
    def get_total_browser_histories(self, request, pk=None):
        """get total  in the app"""
        output = BrowserHistory.objects.count()
        if not output:
            return Response(
                {"success": False, "total_browser_histories": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_browser_histories": output},
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
        url_path='get-total-browser-histories-by-group',
    )
    def get_total_browser_histories_by_group(self, request, pk=None):
        """Get total for an  organization browser_histories by groups"""

        group = request.query_params["group"]
        output = BrowserHistory.objects.filter(group=group).count()
        if not output:
            return Response(
                {"success": False, "total_browser_histories": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_browser_histories": output},
            status=status.HTTP_200_OK,
        )
