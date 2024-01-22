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
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperAdminOrAdmin
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from organization.models import Organization
from group.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from blog.models import Blog, Comment
from in_app_chat.models import InAppChat
from resource.models import Resources, Type
from browser_history.models import BrowserHistory
from forum.models import Forum
from topics.models import Topic
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from simpleblog.utils import calculate_total_engagement_score


def get_count_model_instances(model, organization, group, date_range, additional_filters=None):
    filters = {'organization': organization, 'group': group, 'created_at__range': date_range}
    if additional_filters:
        filters.update(additional_filters)

    try:
        return model.objects.filter(**filters).count()
    except ObjectDoesNotExist:
        return 0


def receive_model_instance(model, organization_id, group, organization, model_name):
    try:
        model_instance = model.objects.filter(organization=organization, group=group).first()
        return model_instance
    except ObjectDoesNotExist:
        return Response(
            {
                "error": f"organization- {organization_id} belonging to group- {group} have no {model_name} activity score ".title()
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class BaseViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "put", "delete"]
    permission_classes = [IsSuperAdminOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'group']
    ordering_fields = ['created_at']

    def get_queryset(self):
        if IsAdmin().has_permission(self.request, self):
            organization = Organization.objects.get(
                organization_id=self.request.user.organization_id
            ).pk
            return self.queryset.filter(organization=organization)
        return super().get_queryset()

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_organization_activity_scores(self, organization_id, group_pk, date_range, pk=None):
        """Get activity score"""

        organization = get_object_or_404(Organization, organization_id=organization_id).pk
        group = get_object_or_404(Group, pk=group_pk).pk

        post_blog = get_count_model_instances(Blog, organization, group, date_range)
        send_chat_message = get_count_model_instances(InAppChat, organization, group, date_range)
        post_forum = get_count_model_instances(Forum, organization, group, date_range)
        image_sharing = get_count_model_instances(
            Resources, organization, group, date_range, {'type__name__icontains': 'Image'}
        )
        video_sharing = get_count_model_instances(
            Resources, organization, group, date_range, {'type__name__icontains': 'Video'}
        )
        text_resource_sharing = get_count_model_instances(
            Resources, organization, group, date_range, {'type__name__icontains': 'Text-Based'}
        )
        created_topic = get_count_model_instances(Topic, organization, group, date_range)
        comment = get_count_model_instances(Comment, organization, group, date_range)
        used_in_app_browser = get_count_model_instances(
            BrowserHistory, organization, group, date_range
        )
        recieve_chat_message = get_count_model_instances(InAppChat, organization, group, date_range)

        tallies = {
            "post_blog": post_blog,
            "send_chat_message": send_chat_message,
            "post_forum": post_forum,
            "image_sharing": image_sharing,
            "video_sharing": video_sharing,
            "text_resource_sharing": text_resource_sharing,
            "created_topic": created_topic,
            "comment": comment,
            "used_in_app_browser": used_in_app_browser,
            "read_blog": 0,
            "read_forum": 0,
            "recieve_chat_message": recieve_chat_message,
            "download_resources": 0,
        }

        socialization_instance = receive_model_instance(
            Socialization, organization_id, group, organization, "Socialization"
        )
        externalization_instance = receive_model_instance(
            Externalization, organization_id, group, organization, "Externalization"
        )
        internalization_instance = receive_model_instance(
            Internalization, organization_id, group, organization, "Internalization"
        )
        combinations_instance = receive_model_instance(
            Combination, organization_id, group, organization, "Combination"
        )

        cec = combinations_instance.calculate_combination_score(tallies)
        sec = socialization_instance.calculate_socialization_score(tallies)
        iec = internalization_instance.calculate_internalization_score(tallies)
        eec = externalization_instance.calculate_externalization_score(tallies)
        tes = calculate_total_engagement_score(sec, eec, cec, iec)

        return {"tes": tes, "sec": sec, "eec": eec, "cec": cec, "iec": iec}


class SocializationViewSets(BaseViewSet):
    serializer_class = SocializationSerializer
    queryset = Socialization.objects.all()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="organization_id",
                description="organization_id",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="group_pk",
                description="group_pk",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="start_date",
                description="Start date in the format 'YYYY-MM-DD'",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="end_date",
                description="End date in the format 'YYYY-MM-DD'",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
    )
    def get_organization_socialization_activity_scores(self, request, pk=None):
        """Get socialization activity score"""
        organization_id = request.query_params["organization_id"]
        group_pk = request.query_params["group_pk"]

        start_date = timezone.make_aware(
            timezone.datetime.strptime(request.query_params["start_date"], "%Y-%m-%d")
        )
        end_date = timezone.make_aware(
            timezone.datetime.strptime(request.query_params["end_date"], "%Y-%m-%d")
        )

        date_range = (start_date, end_date)

        organization = get_object_or_404(Organization, organization_id=organization_id).pk
        group = get_object_or_404(Group, pk=group_pk).pk
        organization_activity_scores = self.get_organization_activity_scores(
            organization_id, group, date_range
        )
        sec = organization_activity_scores["sec"]
        tes = organization_activity_scores["tes"]

        socialization_instance = receive_model_instance(
            Socialization, organization_id, group, organization, "Socialization"
        )
        output = socialization_instance.calculate_socialization_percentage(sec, tes)
        return Response(
            {
                "success": True,
                "socialization_percentage":  round(output, 2),
                "organization_id": organization_id,
                "group": group,
                "start_date": start_date,
                "end_date": end_date,
            },
            status=status.HTTP_200_OK,
        )


class ExternalizationViewSets(BaseViewSet):
    serializer_class = ExternalizationSerializer
    queryset = Externalization.objects.all()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="organization_id",
                description="organization_id",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="group_pk",
                description="group_pk",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="start_date",
                description="Start date in the format 'YYYY-MM-DD'",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="end_date",
                description="End date in the format 'YYYY-MM-DD'",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
    )
    def get_organization_externalization_activity_scores(self, request, pk=None):
        """Get organization externalization activity score"""

        organization_id = request.query_params["organization_id"]
        group_pk = request.query_params["group_pk"]

        start_date = timezone.make_aware(
            timezone.datetime.strptime(request.query_params["start_date"], "%Y-%m-%d")
        )
        end_date = timezone.make_aware(
            timezone.datetime.strptime(request.query_params["end_date"], "%Y-%m-%d")
        )

        date_range = (start_date, end_date)

        organization = get_object_or_404(Organization, organization_id=organization_id).pk
        group = get_object_or_404(Group, pk=group_pk).pk

        organization_activity_scores = self.get_organization_activity_scores(
            organization_id, group, date_range
        )
        eec = organization_activity_scores["eec"]
        tes = organization_activity_scores["tes"]
        externalization_instance = receive_model_instance(
            Externalization, organization_id, group, organization, "Externalization"
        )
        output = externalization_instance.calculate_externalization_percentage(eec, tes)

        return Response(
            {
                "success": True,
                "externalization_percentage":  round(output, 2),
                "organization_id": organization_id,
                "group": group,
                "start_date": start_date,
                "end_date": end_date,
            },
            status=status.HTTP_200_OK,
        )


class InternalizationViewSets(BaseViewSet):
    serializer_class = InternalizationSerializer
    queryset = Internalization.objects.all()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="organization_id",
                description="organization_id",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="group_pk",
                description="group_pk",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="start_date",
                description="Start date in the format 'YYYY-MM-DD'",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="end_date",
                description="End date in the format 'YYYY-MM-DD'",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
    )
    def get_organization_internalization_activity_scores(self, request, pk=None):
        """Get organization activity score"""

        organization_id = request.query_params["organization_id"]
        group_pk = request.query_params["group_pk"]

        start_date = timezone.make_aware(
            timezone.datetime.strptime(request.query_params["start_date"], "%Y-%m-%d")
        )
        end_date = timezone.make_aware(
            timezone.datetime.strptime(request.query_params["end_date"], "%Y-%m-%d")
        )

        date_range = (start_date, end_date)

        organization = get_object_or_404(Organization, organization_id=organization_id).pk
        group = get_object_or_404(Group, pk=group_pk).pk
        organization_activity_scores = self.get_organization_activity_scores(
            organization_id, group, date_range
        )
        iec = organization_activity_scores["iec"]
        tes = organization_activity_scores["tes"]
        internalization_instance = receive_model_instance(
            Internalization, organization_id, group, organization, "Internalization"
        )
        output = internalization_instance.calculate_internalization_percentage(iec, tes)

        return Response(
            {
                "success": True,
                "internalization_percentage":  round(output, 2),
                "organization_id": organization_id,
                "group": group,
                "start_date": start_date,
                "end_date": end_date,
            },
            status=status.HTTP_200_OK,
        )


class CombinationViewSets(BaseViewSet):
    serializer_class = CombinationSerializer
    queryset = Combination.objects.all()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="organization_id",
                description="organization_id",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="group_pk",
                description="group_pk",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="start_date",
                description="Start date in the format 'YYYY-MM-DD'",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="end_date",
                description="End date in the format 'YYYY-MM-DD'",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
    )
    def get_organization_combination_activity_scores(self, request, pk=None):
        """Get organization  combination activity percentage details"""

        organization_id = request.query_params["organization_id"]
        group_pk = request.query_params["group_pk"]

        start_date = timezone.make_aware(
            timezone.datetime.strptime(request.query_params["start_date"], "%Y-%m-%d")
        )
        end_date = timezone.make_aware(
            timezone.datetime.strptime(request.query_params["end_date"], "%Y-%m-%d")
        )

        date_range = (start_date, end_date)

        organization = get_object_or_404(Organization, organization_id=organization_id).pk
        group = get_object_or_404(Group, pk=group_pk).pk

        organization_activity_scores = self.get_organization_activity_scores(
            organization_id, group, date_range
        )
        cec = organization_activity_scores["cec"]
        tes = organization_activity_scores["tes"]
        combination_instance = receive_model_instance(
            Combination, organization_id, group, organization, "Externalization"
        )
        output = combination_instance.calculate_combination_percentage(cec, tes)

        return Response(
            {
                "success": True,
                "combination_percentage": round(output, 2),
                "organization_id": organization_id,
                "group": group,
                "start_date": start_date,
                "end_date": end_date,
            },
            status=status.HTTP_200_OK,
        )
