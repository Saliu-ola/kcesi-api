from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from .models import Forum, ForumComment,CommentReplies
from .serializers import ForumSerializer,ForumCreateSerializer, ForumCommentSerializer,CommentReplySerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperAdminOrAdmin
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import cloudinary.uploader
from django.db.models import F, Value, CharField, Q
from organization.models import Organization
from topics.serializers import ForumTopicSerializer
from group.models import Group, UserGroup

class ForumViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = ForumSerializer
    permission_classes = [IsAuthenticated]
    queryset = (
        Forum.objects.all()
        .prefetch_related('resources')
        .select_related('user', 'organization', 'group', 'category')
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'user', 'organization', 'group', "start_time", "end_time"]
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
                Q(user_id=user.id)
            ).distinct()

        else:
            raise ValueError("Role id not present")

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = serializer.save()
            forum = result['forum']
            forum_topic = result['forum_topic']
            forum_topic_created = result['forum_topic_created']

            response_data = {
                'success': True,
                'message': 'Forum created successfully',
                'forum': ForumCreateSerializer(forum,  context={'request': request}).data,
                'forum_topic': ForumTopicSerializer(forum_topic).data,
                # 'forum_topic': forum_topic,
                'forum_topic_created': forum_topic_created
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error occurred: {str(e)}',
            }, status=status.HTTP_400_BAD_REQUEST)


    def perform_destroy(self, instance):

        for resource in instance.resources.all():
            cloudinary.uploader.destroy(resource.cloud_id)
        instance.delete()

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return ForumSerializer
        return ForumCreateSerializer

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
        url_path='get-total-forums-by-organization',
    )
    def get_total_forums_by_organization(self, request, pk=None):
        """Get total forums for an organization"""

        organization = request.query_params["organization"]

        output = Forum.objects.filter(organization=organization).count()
        if not output:
            return Response(
                {"success": False, "total_forums": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_forums": output},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-forums',
    )
    def get_total_forums(self, request, pk=None):
        """get total forums in the app"""
        output = Forum.objects.count()
        if not output:
            return Response(
                {"success": False, "total_forums": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_forums": output},
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
        url_path='get-total-forums-by-group',
    )
    def get_total_forums_by_group(self, request, pk=None):
        """Get total for an  organization forums by groups"""

        group = request.query_params["group"]
        output = Forum.objects.filter(group=group).count()
        if not output:
            return Response(
                {"success": False, "total_forums": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_forums": output},
            status=status.HTTP_200_OK,
        )


class CommentViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = ForumCommentSerializer
    permission_classes = [IsAuthenticated]
    queryset = ForumComment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'organization', 'forum', 'group']
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
    serializer_class = CommentReplySerializer
    permission_classes = [IsAuthenticated]
    queryset = CommentReplies.objects.all()
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
