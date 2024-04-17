from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from .models import Feedback
from .serializers import FeedbackListSerializer, FeedbackCreateSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperAdminOrAdmin
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from organization.models import Organization
from rest_framework.parsers import MultiPartParser, FormParser


class FeedbackViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = FeedbackCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Feedback.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'author',
        'recipent_type',
        'concerned_organization',
        'concerned_group',
        'concerned_platform',
    ]
    search_fields = ['content']
    ordering_fields = ['created_at']
    parser_classes = [MultiPartParser]

    def perform_create(self, serializer):
        author = self.request.user
        serializer.save(author=author)

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return FeedbackListSerializer
        return FeedbackCreateSerializer
