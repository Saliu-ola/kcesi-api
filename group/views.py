from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import AllowAny , IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from organization.models import Organization
from .models import Group, UserGroup 
from .serializers import (
    GroupAISerializer,
    GroupSerializer,
    UserGroupListSerializer,
    UserGroupCreateSerializer,
    UpdateUserGroupSerializer,
    
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperAdminOrAdmin
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from simpleblog.ai import (
    get_foreign_terms,get_percentage_relevancy,
    check_percentage_relevance_of_uncommon_words,
)

from groupleader.models import *

class GroupViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = GroupSerializer
    permission_classes = [AllowAny]
    queryset = Group.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'title',
        'organization_id',
    ]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at']

    ADMIN_ROLE_ID = 2
    SUPER_ADMIN_ROLE_ID = 1
    USER_ROLE_ID = 3

    def get_queryset(self):
        if self.request.user.role_id == self.SUPER_ADMIN_ROLE_ID:
            return self.queryset
        elif self.request.user.role_id in [self.ADMIN_ROLE_ID, self.USER_ROLE_ID]:
            return self.queryset.filter(organization_id=self.request.user.organization_id)

        else:
            raise ValueError("Role id not present")

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=['POST'],
        detail=True,
        permission_classes=[AllowAny],
        serializer_class=GroupAISerializer,
        url_path='check-relevance',
    )
    def check_relevance(self, request, pk=None):
        """To check relevance of input texts to group description"""
        try:
            group = self.get_object()
            serializer = GroupAISerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_content = serializer.data["content"]
            # existing_text = group.related_terms
            # Conditionally assign existing_text based on library type
            existing_text = group.related_terms if LibraryOption.library_type == 'AI' else group.related_terms_library_b
            uncommon_text = get_foreign_terms(new_content,existing_text)

            # decided to add the new incoming that are relevant before getting final relevace
            if uncommon_text:
                score = check_percentage_relevance_of_uncommon_words(uncommon_text, group.content)
                score = float(score)
                if score >= 45:
                    existing_text.extend(uncommon_text)
                    if LibraryOption.library_type == 'AI':
                        group.related_terms = existing_text
                    else:
                        group.related_terms_library_b = existing_text
                    group.save()

            if LibraryOption.library_type == 'AI':
                updated_text = group.related_terms
            else:
                updated_text = group.related_terms_library_b
      
            # so i fetch the updated one along
            relevant_percentage = get_percentage_relevancy(new_content, updated_text)
            relevant_percentage = float(relevant_percentage)

            rating = 'Very Bad'
            if relevant_percentage > 59:
                rating = 'Excellent'
            elif relevant_percentage > 49:
                rating = 'Very Good'
            elif relevant_percentage > 29:
                rating = 'Good'
            elif relevant_percentage > 14:
                rating = 'Fair'
            elif relevant_percentage > 10:
                rating = 'Bad'

            response = {"relevancy_percentage": relevant_percentage, "rating": rating}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserGroupsViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "delete"]
    serializer_class = UserGroupCreateSerializer
    permission_classes = [AllowAny]
    queryset = UserGroup.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'user__organization_name', 'groups']
    ordering_fields = ['created_at']

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return UserGroupListSerializer
        elif self.action == "add":
            return UpdateUserGroupSerializer
        return UserGroupCreateSerializer

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=UpdateUserGroupSerializer,
        url_path='add-group',
    )
    def add(self, request, pk=None):
        serializer = UpdateUserGroupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]
            user_group_instance = get_object_or_404(UserGroup, user=user)
            initial_groups = user_group_instance.groups.all()
            new_groups = serializer.validated_data["groups"]
            user_group_instance.groups.set(list(initial_groups) + list(new_groups))

            return Response(UserGroupCreateSerializer(user_group_instance).data)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=UpdateUserGroupSerializer,
        url_path='remove-group',
    )
    def remove(self, request, pk=None):
        serializer = UpdateUserGroupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]
            user_group_instance = get_object_or_404(UserGroup, user=user)
            groups_to_remove = serializer.validated_data["groups"]
            user_group_instance.groups.remove(*groups_to_remove)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(UserGroupCreateSerializer(user_group_instance).data)



