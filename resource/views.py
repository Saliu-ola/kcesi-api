from rest_framework.request import Request
from rest_framework.response import Response

from organization.models import Organization
from .models import Resources
from .serializers import ResourcesSerializer, CreateResourcesSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import cloudinary.uploader
from rest_framework.parsers import MultiPartParser
from accounts.permissions import IsSuperAdmin
from .serializers import ResourceFileSizeSerializer
from .models import ResourceFileSize


class ResourcesViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = ResourcesSerializer
    permission_classes = [IsAuthenticated]
    queryset = Resources.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'size', 'organization', 'group', 'sender', 'receiver']
    search_fields = ['title']
    ordering_fields = ['created_at']
    parser_classes = [MultiPartParser]

    def perform_destroy(self, instance):
        cloudinary.uploader.destroy(instance.cloud_id)
        instance.delete()
    
    ADMIN_ROLE_ID = 2
    SUPER_ADMIN_ROLE_ID = 1  
    USER_ROLE_ID = 3

    def get_queryset(self):
        if self.request.user.role_id == self.SUPER_ADMIN_ROLE_ID:
            return self.queryset
        elif self.request.user.role_id in [self.ADMIN_ROLE_ID,self.USER_ROLE_ID]:
            organization_id = self.request.user.organization_id
            organization = Organization.objects.filter(organization_id=organization_id).first()
            return self.queryset.filter(organization=organization)
        
    def get_serializer_class(self):
        if self.action in ['update', 'create', 'partial_update']:
            return CreateResourcesSerializer
        return ResourcesSerializer

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
        output = Resources.objects.filter(group=group, type=resource_type).count()
        if not output:
            return Response(
                {"success": False, "total_resources": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_resources": output},
            status=status.HTTP_200_OK,
        )




class FileSizeCreateView(generics.CreateAPIView):
    permission_classes = [IsSuperAdmin]
    queryset = ResourceFileSize.objects.all()
    serializer_class = ResourceFileSizeSerializer

    def create(self, request, *args, **kwargs):
        file_type = request.data.get('file_type')
        if ResourceFileSize.objects.filter(file_type=file_type).exists():
            return Response({"detail": "File type already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
    


class FileSizeUpdateView(generics.UpdateAPIView):
    permission_classes = [IsSuperAdmin]
    queryset = ResourceFileSize.objects.all()
    serializer_class = ResourceFileSizeSerializer

    def update(self, request, *args, **kwargs):
        file_type = request.data.get('file_type')
        instance = ResourceFileSize.objects.filter(file_type=file_type).first()
        if not instance:
            return Response({"detail": "File type not Initialized. Create one at resources/filesize/create/ "}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    

# class FileSizeRetrieveView(generics.RetrieveAPIView):
#     permission_classes = [IsSuperAdmin]
#     queryset = ResourceFileSize.objects.all()
#     serializer_class = ResourceFileSizeSerializer

#     def retrieve(self, request, *args, **kwargs):
#         file_type = request.data.get('file_type')
#         instance = ResourceFileSize.objects.filter(file_type=file_type).first()
#         if not instance:
#             return Response({"detail": "File type not found."}, status=status.HTTP_404_NOT_FOUND)
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)
    


class FileSizeRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ResourceFileSize.objects.all()
    serializer_class = ResourceFileSizeSerializer
    lookup_field = 'file_type'
    lookup_url_kwarg = 'file_type'

    
class FileSizeListView(generics.ListAPIView):
    pagination_class = None
    permission_classes = [IsSuperAdmin]
    queryset = ResourceFileSize.objects.all()
    serializer_class = ResourceFileSizeSerializer