from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from .models import Blog, Comment
from .serializers import BlogSerializer, CommentSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperOrAdminAdmin
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class BlogViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = BlogSerializer
    permission_classes = [IsSuperOrAdminAdmin]
    queryset = Blog.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author', 'organization', 'group']
    search_fields = ['topic']
    ordering_fields = ['created_at']

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # @extend_schema(
    #     parameters=[
    #         OpenApiParameter(
    #             name="organization_id",
    #             description="organization_id",
    #             required=True,
    #             type=OpenApiTypes.STR,
    #         ),
    #     ],
    #     responses={200: None},
    # )
    # @action(
    #     methods=['GET'],
    #     detail=False,
    #     serializer_class=None,
    #     url_path='get-total-blogs-by-organization',
    # )
    # def get_total_blogs_by_organization_id(self, request, pk=None):
    #     """Get total blogs for an  organization members"""

    #     organization_id = request.query_params["organization"]
    #     output = Blog.objects.filter(organization_id=organization_id).count()
    #     return Response(
    #         {"success": True, "total_members": output},
    #         status=status.HTTP_200_OK,
    #     )

    # @action(
    #     methods=['GET'],
    #     detail=False,
    #     serializer_class=None,
    #     url_path='get-total-organization-members',
    # )
    # def get_total_members(self, request, pk=None):
    #     """get total members in the app"""
    #     output = User.objects.count()
    #     return Response(
    #         {"success": True, "total_members": output},
    #         status=status.HTTP_200_OK,
    #     )

    # @extend_schema(
    #     parameters=[
    #         OpenApiParameter(
    #             name="group_id",
    #             description="group_id",
    #             required=True,
    #             type=OpenApiTypes.STR,
    #         ),
    #     ],
    #     responses={200},
    # )
    # @action(
    #     methods=['GET'],
    #     detail=False,
    #     serializer_class=None,
    #     url_path='get-total-members-by-group',
    # )
    # def get_total_members_by_group(self, request, pk=None):
    #     """Get total for an  organization members by groups"""

    #     group_id = request.query_params["group_id"]
    #     output = User.objects.filter(group_id=group_id).count()
    #     return Response(
    #         {"success": True, "total_members": output},
    #         status=status.HTTP_200_OK,
    #     )


class CommentViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = CommentSerializer
    permission_classes = [IsSuperOrAdminAdmin]
    queryset = Comment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'organization', 'blog', 'Platform', 'group']
    search_fields = ['content']
    ordering_fields = ['created_at']

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
