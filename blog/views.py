from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from .models import Blog, Comment,BlogCommentReplies, BlogRead
from organization.models import Organization
from group.models import Group, UserGroup
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperAdminOrAdmin
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import F, Value, CharField, Q
from django.db.models.functions import Concat
import cloudinary.uploader
from topics.serializers import BlogTopicSerializer

class BlogViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = BlogListSerializer
    queryset = (
        Blog.objects.all()
        .prefetch_related('resources')
        .select_related('author', 'organization', 'group', 'category')
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'category',
        'category__name',
        'author',
        'organization',
        'organization__name',
        'group',
        'group__title',
    ]
    search_fields = ['topic']
    ordering_fields = ['created_at']

    ADMIN_ROLE_ID = 2
    SUPER_ADMIN_ROLE_ID = 1  
    USER_ROLE_ID = 3

    def get_queryset(self):
        user = self.request.user
        organization_id = self.request.user.organization_id
        organization = Organization.objects.filter(organization_id=organization_id).first()
        if self.request.user.role_id == self.SUPER_ADMIN_ROLE_ID:
            return self.queryset
        
        elif user.role_id == self.ADMIN_ROLE_ID:
            return self.queryset.filter(organization=organization)
        
        elif user.role_id == self.USER_ROLE_ID:
            user_groups = UserGroup.objects.filter(user=user).values_list('groups', flat=True)
            
            return self.queryset.filter(
                Q(organization=organization, group_id__in=user_groups) |
                Q(author_id=user.id)
            ).distinct()

        # elif self.request.user.role_id in [self.ADMIN_ROLE_ID,self.USER_ROLE_ID]:
        #     organization_id = self.request.user.organization_id
        #     organization = Organization.objects.filter(organization_id=organization_id).first()
        #     return self.queryset.filter(organization=organization)
        
        else:
            raise ValueError("Role id not present")

    def perform_destroy(self, instance):

        for resource in instance.resources.all():
            cloudinary.uploader.destroy(resource.cloud_id)
        instance.delete()

    def perform_create(self, serializer):
        author = self.request.user
        serializer.save(author=author)

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return BlogListSerializer
        return BlogCreateSerializer

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = serializer.save(author=request.user)
            blog = result['blog']
            blog_topic = result['blog_topic']
            blog_topic_created = result['blog_topic_created']

            response_data = {
                'success': True,
                'message': 'Blog and BlogTopic created successfully',
                'blog': BlogCreateSerializer(blog, context={'request': request}).data,
                # 'blog_topic': blog_topic,
                'blog_topic': BlogTopicSerializer(blog_topic).data,
                'blog_topic_created': blog_topic_created
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error occurred: {str(e)}',
            }, status=status.HTTP_400_BAD_REQUEST)

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
        url_path='get-total-blogs-by-organization',
    )
    def get_total_blogs_by_organization(self, request, pk=None):
        """Get total blogs for an organization"""

        organization = request.query_params["organization"]

        output = Blog.objects.filter(organization=organization).count()
        if not output:
            return Response(
                {"success": False, "total_blogs": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_blogs": output},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-blogs',
    )
    def get_total_blogs(self, request, pk=None):
        """get total blogs in the app"""
        output = Blog.objects.count()
        if not output:
            return Response(
                {"success": False, "total_blogs": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_blogs": output},
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
        url_path='get-total-blogs-by-group',
    )
    def get_total_blogs_by_group(self, request, pk=None):
        """Get total for an  organization blogs by groups"""

        group = request.query_params["group"]
        output = Blog.objects.filter(group=group).count()
        if not output:
            return Response(
                {"success": False, "total_blogs": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_blogs": output},
            status=status.HTTP_200_OK,
        )


class CommentViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Comment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'organization', 'blog', 'group']
    search_fields = ['content']
    ordering_fields = ['created_at']

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ReplyViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = BlogCommentReplySerializer
    permission_classes = [IsAuthenticated]
    queryset = BlogCommentReplies.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'organization', 'comment', 'group']
    search_fields = ['content']
    ordering_fields = ['created_at']

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BlogReadViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = BlogReadListSerializer
    queryset = BlogRead.objects.all().select_related('user', 'blog', 'group', 'organization')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'blog', 'group', 'organization']
    search_fields = ['blog__topic']
    ordering_fields = ['created_at']

    ADMIN_ROLE_ID = 2
    SUPER_ADMIN_ROLE_ID = 1
    USER_ROLE_ID = 3

    def get_queryset(self):
        user = self.request.user
        organization_id = user.organization_id
        organization = Organization.objects.filter(organization_id=organization_id).first()

        if user.role_id == self.SUPER_ADMIN_ROLE_ID:
            return self.queryset
        elif user.role_id == self.ADMIN_ROLE_ID:
            return self.queryset.filter(organization=organization)
        elif user.role_id == self.USER_ROLE_ID:
            user_groups = UserGroup.objects.filter(user=user).values_list('groups', flat=True)
            return self.queryset.filter(
                Q(organization=organization, group_id__in=user_groups) |
                Q(user=user)
            ).distinct()
        else:
            raise ValueError("Role id not present")

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return BlogReadListSerializer
        return BlogReadCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
    
        user = request.user
        blog = serializer.validated_data['blog']

        if BlogRead.objects.filter(user=user, blog=blog).exists():
            return Response({
                'success': True,
                'message': 'User has already read this blog.'
            }, status=status.HTTP_200_OK)
  
        try:
            blog_read = serializer.save(user=request.user)
            response_data = {
                'success': True,
                'message': 'BlogRead created successfully',
                'blog_read': BlogReadListSerializer(blog_read, context={'request': request}).data,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error occurred: {str(e)}',
            }, status=status.HTTP_400_BAD_REQUEST)

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
        url_path='get-total-blog-reads-by-organization',
    )
    def get_total_blog_reads_by_organization(self, request, pk=None):
        """Get total blog reads for an organization"""
        organization = request.query_params["organization"]
        output = BlogRead.objects.filter(organization=organization).count()
        if not output:
            return Response(
                {"success": False, "total_blog_reads": 0},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": True, "total_blog_reads": output},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-blog-reads',
    )
    def get_total_blog_reads(self, request, pk=None):
        """get total blog reads in the app"""
        output = BlogRead.objects.count()
        if not output:
            return Response(
                {"success": False, "total_blog_reads": 0},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": True, "total_blog_reads": output},
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
        url_path='get-total-blog-reads-by-group',
    )
    def get_total_blog_reads_by_group(self, request, pk=None):
        """Get total blog reads for an organization by groups"""
        group = request.query_params["group"]
        output = BlogRead.objects.filter(group=group).count()
        if not output:
            return Response(
                {"success": False, "total_blog_reads": 0},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": True, "total_blog_reads": output},
            status=status.HTTP_200_OK,
        )

