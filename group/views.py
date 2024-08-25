from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from simpleblog.pagination import CustomPagination

from organization.models import Organization
from .models import Group, UserGroup
from .serializers import (
    GroupAISerializer,
    GroupSerializer,
    UserGroupListSerializer,
    UserGroupCreateSerializer,
    UpdateUserGroupSerializer,
    UserGroupSerializer,
    UsersInGroupListSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperAdminOrAdmin
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from simpleblog.ai import (
    get_foreign_terms,
    get_percentage_relevancy,
    check_percentage_relevance_of_uncommon_words,
    fetch_update_related_terms
)

from groupleader.models import *
from drf_spectacular.utils import extend_schema, OpenApiParameter

class GroupViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = GroupSerializer
    permission_classes = [AllowAny]
    queryset = Group.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "title",
        "organization_id",
    ]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at"]

    ADMIN_ROLE_ID = 2
    SUPER_ADMIN_ROLE_ID = 1
    USER_ROLE_ID = 3

    def get_queryset(self):
        if self.request.user.role_id == self.SUPER_ADMIN_ROLE_ID:
            return self.queryset
        elif self.request.user.role_id in [self.ADMIN_ROLE_ID, self.USER_ROLE_ID]:
            return self.queryset.filter(
                organization_id=self.request.user.organization_id
            )

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
        methods=["POST"],
        detail=True,
        permission_classes=[AllowAny],
        serializer_class=GroupAISerializer,
        url_path="check-relevance",
    )
    def check_relevance(self, request, pk=None):
        """To check relevance of input texts to group description"""
        try:
            group = self.get_object()

            library_option = LibraryOption.objects.get(group=group)
            library_type = library_option.library_type

            serializer = GroupAISerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_content = serializer.data["content"]
            # existing_text = group.related_terms
            # Conditionally assign existing_text based on library type
            if library_type == "AI":
                existing_text = group.related_terms if group.related_terms else []
            else:
                existing_text = group.related_terms_library_b if group.related_terms_library_b else []

            # so i fetch the updated one along
            relevant_percentage = get_percentage_relevancy(new_content, existing_text)
            relevant_percentage = float(relevant_percentage) *2

            rating = "Very Bad"
            if relevant_percentage > 59:
                rating = "Excellent"
            elif relevant_percentage > 49:
                rating = "Very Good"
            elif relevant_percentage > 29:
                rating = "Good"
            elif relevant_percentage > 14:
                rating = "Fair"
            elif relevant_percentage > 10:
                rating = "Bad"
  #background update of the AI library so far it meets this requirements
            if (
                relevant_percentage >= 50
                and len(new_content.split()) > 20
                and LibraryOption.library_type == "AI"
            ):
                uncommon_text = get_foreign_terms(new_content, existing_text)
                if uncommon_text:
                    # Fetch new related terms using Gemini API
                    new_related_terms = fetch_update_related_terms(new_content)

                    # Remove common terms to avoid duplication
                    updated_related_terms = [
                        term for term in new_related_terms if term not in existing_text
                    ]

                    # Update the related terms and save the group
                    group.related_terms.extend(updated_related_terms)
                    group.save()

            response = {"relevancy_percentage": relevant_percentage, "rating": rating}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserGroupsViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "delete"]
    serializer_class = UserGroupCreateSerializer
    permission_classes = [AllowAny]
    queryset = UserGroup.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["user", "user__organization_name", "groups"]
    ordering_fields = ["created_at"]

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
        methods=["POST"],
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=UpdateUserGroupSerializer,
        url_path="add-group",
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
        methods=["POST"],
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=UpdateUserGroupSerializer,
        url_path="remove-group",
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


class UserGroupsView(generics.ListAPIView):
    serializer_class = UserGroupSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return UserGroup.objects.filter(user_id=user_id ).prefetch_related("groups")
    


class UsersInGroupView(generics.ListAPIView):
    serializer_class = UsersInGroupListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        return UserGroup.objects.filter(groups__id=group_id)





class SearchGroupRelatedTermsView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='library_type', description='Type of library (a or b)', required=True, type=str),
            OpenApiParameter(name='term', description='Search term for related words', required=True, type=str),
        ],
        responses={200: dict, 404: dict, 400: dict, 500: dict},
        description='Search for related terms in a specific Group and library type'
    )
    def get(self, request, group_id):
        library_type = request.query_params.get('library_type')
        search_term = request.query_params.get('term', '').lower()

        if not library_type or not search_term:
            return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = Group.objects.get(id=group_id)
            
            if library_type == 'a':
                related_terms = group.related_terms
            elif library_type == 'b':
                related_terms = group.related_terms_library_b
            else:
                return Response({'error': 'Invalid library type'}, status=status.HTTP_400_BAD_REQUEST)

            if not related_terms:
                return Response({'error': 'No related terms found for this group and library type'}, status=status.HTTP_404_NOT_FOUND)

            matching_terms = [term for term in related_terms if search_term in term.lower()]

            paginator = CustomPagination()
            paginated_terms = paginator.paginate_queryset(matching_terms, request)
            
            return paginator.get_paginated_response({'results': paginated_terms})
        
        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
