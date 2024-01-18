from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from .models import Socialization, Internalization, Externalization, Combination
from .serializer import (
    CombinationSerializer,
    InternalizationSerializer,
    SocializationSerializer,
    ExternalizationSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperOrAdminAdmin
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from organization.models import Organization
from group.models import Group


class SocializationViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = SocializationSerializer
    permission_classes = [IsAdmin]
    queryset = Socialization.objects.all()
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsSuperOrAdminAdmin()]

        return super().get_permissions()

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ExternalizationViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = ExternalizationSerializer
    permission_classes = [IsAdmin]
    queryset = Externalization.objects.all()
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsSuperOrAdminAdmin()]

        return super().get_permissions()

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class InternalizationViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = InternalizationSerializer
    permission_classes = [IsAdmin]
    queryset = Internalization.objects.all()
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsSuperOrAdminAdmin()]

        return super().get_permissions()

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CombinationViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = CombinationSerializer
    permission_classes = [IsAdmin]
    queryset = Combination.objects.all()
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsSuperOrAdminAdmin()]

        return super().get_permissions()

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
