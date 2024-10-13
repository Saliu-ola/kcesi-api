from rest_framework.request import Request
from rest_framework.response import Response
from .models import Organization
from .serializers import OrganizationSerializer , UserSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperAdminOrAdmin
from accounts.models import User
import django_filters

class OrganizationFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Organization
        fields = ['name', 'organization_id', 'start_date', 'end_date']


class OrganizationViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    serializer_class = OrganizationSerializer
    permission_classes = [IsSuperAdminOrAdmin]
    queryset = Organization.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = [
    #     'name',
    #     'organization_id',
    # ]
    filterset_class = OrganizationFilter 
    search_fields = ['name']
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


class UserListByOrganization(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        return User.objects.filter(organization_id=organization_id)
