from rest_framework.request import Request
from rest_framework.response import Response
from .models import Topic
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperAdminOrAdmin
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import AllowAny, IsAuthenticated
from itertools import chain

class TopicViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]
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



class BlogTopicViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = BlogTopicSerializer  
    permission_classes = [IsAuthenticated]
    queryset = BlogTopic.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['title', 'author', 'blog', 'organization', 'group']
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
        ],
        responses={200: None},
    )
    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-blogtopics-by-organization',
    )
    def get_total_blogtopics_by_organization(self, request, pk=None):
        """Get total blog topics for an organization"""
        organization = request.query_params["organization"]
        output = BlogTopic.objects.filter(organization=organization).count()
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
        url_path='get-total-blogtopics',
    )
    def get_total_blogtopics(self, request, pk=None):
        """get total blog topics in the app"""
        output = BlogTopic.objects.count()
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
        url_path='get-total-blogtopics-by-group',
    )
    def get_total_blogtopics_by_group(self, request, pk=None):
        """Get total blog topics for an organization by groups"""
        group = request.query_params["group"]
        output = BlogTopic.objects.filter(group=group).count()
        if not output:
            return Response(
                {"success": False, "total_topics": 0},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": True, "total_topics": output},
            status=status.HTTP_200_OK,
        )



class ForumTopicViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = ForumTopicSerializer  
    permission_classes = [IsAuthenticated]
    queryset = ForumTopic.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['title', 'author', 'forum', 'organization', 'group']
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
        ],
        responses={200: None},
    )
    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-forumtopics-by-organization',
    )
    def get_total_forumtopics_by_organization(self, request, pk=None):
        """Get total forum topics for an organization"""
        organization = request.query_params["organization"]
        output = ForumTopic.objects.filter(organization=organization).count()
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
        url_path='get-total-forumtopics',
    )
    def get_total_forumtopics(self, request, pk=None):
        """get total forum topics in the app"""
        output = ForumTopic.objects.count()
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
        url_path='get-total-forumtopics-by-group',
    )
    def get_total_forumtopics_by_group(self, request, pk=None):
        """Get total forum topics for an organization by groups"""
        group = request.query_params["group"]
        output = ForumTopic.objects.filter(group=group).count()
        if not output:
            return Response(
                {"success": False, "total_topics": 0},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": True, "total_topics": output},
            status=status.HTTP_200_OK,
        )


class CombinedTopicListView(generics.ListAPIView):
    serializer_class = CombinedTopicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        blog_topics = BlogTopic.objects.all()
        forum_topics = ForumTopic.objects.all()

        organization_id = self.request.query_params.get('organization')
        group_id = self.request.query_params.get('group')
        topic_type = self.request.query_params.get('topic_type')
        author_id = self.request.query_params.get('author_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if organization_id:
            blog_topics = blog_topics.filter(organization_id=organization_id)
            forum_topics = forum_topics.filter(organization_id=organization_id)

        if group_id:
            blog_topics = blog_topics.filter(group_id=group_id)
            forum_topics = forum_topics.filter(group_id=group_id)

        if author_id:
            blog_topics = blog_topics.filter(author_id=author_id)
            forum_topics = forum_topics.filter(author_id=author_id)

        if start_date:
            start_datetime = parse_datetime(start_date)
            if start_datetime:
                blog_topics = blog_topics.filter(created_at__gte=start_datetime)
                forum_topics = forum_topics.filter(created_at__gte=start_datetime)

        if end_date:
            end_datetime = parse_datetime(end_date)
            if end_datetime:
                blog_topics = blog_topics.filter(created_at__lte=end_datetime)
                forum_topics = forum_topics.filter(created_at__lte=end_datetime)


        if topic_type == 'blog':
            forum_topics = ForumTopic.objects.none()
        elif topic_type == 'forum':
            blog_topics = BlogTopic.objects.none()
        
        combined_topics = sorted(
            chain(blog_topics, forum_topics),
            key=lambda instance: instance.created_at,
            reverse=True
        )
        
        
        return combined_topics