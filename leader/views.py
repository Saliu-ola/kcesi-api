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
    SocializationUpdaterSerializer,
    ExternalizationUpdaterSerializer,
    CombinationUpdaterSerializer,
    InternalizationUpdaterSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperAdminOrAdmin, IsAdminOrUser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from organization.models import Organization
from group.models import Group, UserGroup
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from blog.models import Blog, Comment
from in_app_chat.models import InAppChat
from resource.models import Resources
from browser_history.models import BrowserHistory
from forum.models import Forum
from topics.models import Topic
from django.utils import timezone
from simpleblog.utils import calculate_total_engagement_score
from accounts.models import User
from rest_framework.exceptions import ValidationError


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

    def get_count_model_instances(self, model, organization, group, date_range, kwargs):
        filters = {'organization': organization, 'group': group.pk, 'created_at__range': date_range}

        if kwargs:
            filters.update(**kwargs)

        count = model.objects.filter(**filters).count()
        return count

    def receive_model_instance(self, model, organization_id, group, organization, model_name):
        try:
            model_instance = model.objects.get(organization=organization, group=group.pk)
            return model_instance
        except model.DoesNotExist:
            raise ValidationError(
                detail=f"Group- {group.title} belonging to organization- {organization_id} have no {model_name} activity score ",
                code=status.HTTP_400_BAD_REQUEST,
            )

    def get_organization_activity_scores(
        self, organization_id, group_pk, user, date_range, pk=None
    ):
        """Get activity score"""

        organization = get_object_or_404(Organization, organization_id=organization_id).pk
        group = get_object_or_404(Group, pk=group_pk)

        post_blog = self.get_count_model_instances(
            Blog, organization, group, date_range, {'author': user}
        )
        send_chat_message = self.get_count_model_instances(
            InAppChat, organization, group, date_range, {'sender': user}
        )
        post_forum = self.get_count_model_instances(
            Forum, organization, group, date_range, {'user': user}
        )
        image_sharing = self.get_count_model_instances(
            Resources,
            organization,
            group,
            date_range,
            {'type': 'IMAGE', 'sender': user},
        )
        video_sharing = self.get_count_model_instances(
            Resources,
            organization,
            group,
            date_range,
            {'type': 'VIDEO', 'sender': user},
        )
        text_resource_sharing = self.get_count_model_instances(
            Resources,
            organization,
            group,
            date_range,
            {'type': 'DOCUMENT', 'sender': user},
        )
        created_topic = self.get_count_model_instances(
            Topic, organization, group, date_range, {'author': user}
        )
        comment = self.get_count_model_instances(
            Comment,
            organization,
            group,
            date_range,
            {'user': user},
        )
        used_in_app_browser = self.get_count_model_instances(
            BrowserHistory,
            organization,
            group,
            date_range,
            {'user': user},
        )
        recieve_chat_message = self.get_count_model_instances(
            InAppChat,
            organization,
            group,
            date_range,
            {'receiver': user},
        )

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

        socialization_instance = self.receive_model_instance(
            Socialization, organization_id, group, organization, "Socialization"
        )

        externalization_instance = self.receive_model_instance(
            Externalization, organization_id, group, organization, "Externalization"
        )

        internalization_instance = self.receive_model_instance(
            Internalization, organization_id, group, organization, "Internalization"
        )
        combinations_instance = self.receive_model_instance(
            Combination, organization_id, group, organization, "Combination"
        )

        cec = combinations_instance.calculate_combination_score(tallies)
        sec = socialization_instance.calculate_socialization_score(tallies)
        iec = internalization_instance.calculate_internalization_score(tallies)
        eec = externalization_instance.calculate_externalization_score(tallies)

        tes = calculate_total_engagement_score(sec, eec, cec, iec)

        return {
            "socialization_instance": socialization_instance,
            "externalization_instance": externalization_instance,
            "combinations_instance": combinations_instance,
            "internalization_instance": internalization_instance,
            "tes": tes,
            "sec": sec,
            "eec": eec,
            "cec": cec,
            "iec": iec,
        }


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
        permission_classes=[IsAdminOrUser],
        serializer_class=None,
    )
    def get_organization_socialization_activity_scores(self, request, pk=None):
        """Get organization activity leaders for socialization"""

        organization_id = request.query_params["organization_id"]
        group_pk = request.query_params["group_pk"]

        start_date = timezone.datetime.strptime(request.query_params["start_date"], "%Y-%m-%d")
        end_date = timezone.datetime.strptime(request.query_params["end_date"], "%Y-%m-%d")

        date_range = (start_date, end_date)

        try:
            group = Group.objects.get(pk=group_pk)
        except ObjectDoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': "group not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        users_in_group = UserGroup.objects.filter(groups=group.pk).values_list("user", flat=True)

        if not users_in_group:
            return Response(
                {
                    'success': True,
                    'message': f"{group.title} group has no member(s) attached",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        leaders = []
        for user in users_in_group:
            organization_activity_scores = self.get_organization_activity_scores(
                organization_id, group.pk, user, date_range
            )
            sec = organization_activity_scores["sec"]
            tes = organization_activity_scores["tes"]

            socialization_instance = organization_activity_scores["socialization_instance"]

            socialization_percentage = round(
                socialization_instance.calculate_socialization_percentage(sec, tes), 2
            )

            user, percentage = user, socialization_percentage

            leaders.append({"user": User.objects.get(pk=user).full_name, "percentage": percentage})

        leaders_sorted = sorted(leaders, key=lambda leader: leader['percentage'], reverse=True)

        return Response(
            {
                "success": True,
                "leaders": leaders_sorted[:10],
                "organization_id": organization_id,
                "group": group.pk,
                "start_date": start_date,
                "end_date": end_date,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="organization_id",
                description="organization_id",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    @action(
        methods=['POST'],
        detail=False,
        permission_classes=[IsAdminOrUser],
        serializer_class=SocializationUpdaterSerializer,
        url_path="set-general-socialization-activities-score",
    )
    def set_general_activities_score_for_organization_socialization(self, request, pk=None):
        organization_id = request.query_params["organization_id"]
        organization = get_object_or_404(Organization, organization_id=organization_id)
        serializer = SocializationUpdaterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            socialization_instances = Socialization.objects.filter(organization=organization)
            socialization_instances.update(**serializer.validated_data)

            return Response(
                {
                    "success": True,
                    "data": SocializationSerializer(socialization_instances, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        permission_classes=[IsAdminOrUser],
        serializer_class=None,
    )
    def get_organization_externalization_activity_scores(self, request, pk=None):
        """Get organization activity leaders for externalization"""

        organization_id = request.query_params["organization_id"]
        group_pk = request.query_params["group_pk"]

        start_date = timezone.make_aware(
            timezone.datetime.strptime(request.query_params["start_date"], "%Y-%m-%d")
        )
        end_date = timezone.make_aware(
            timezone.datetime.strptime(request.query_params["end_date"], "%Y-%m-%d")
        )

        date_range = (start_date, end_date)

        try:
            group = Group.objects.get(pk=group_pk)
        except ObjectDoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': "group not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        users_in_group = UserGroup.objects.filter(groups=group.pk).values_list("user", flat=True)

        if not users_in_group:
            return Response(
                {
                    'success': True,
                    'message': f"{group.title} group has no member(s) attached",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        leaders = []
        for user in users_in_group:
            organization_activity_scores = self.get_organization_activity_scores(
                organization_id, group.pk, user, date_range
            )
            eec = organization_activity_scores["eec"]
            tes = organization_activity_scores["tes"]

            externalization_instance = organization_activity_scores["externalization_instance"]
            externalization_percentage = round(
                externalization_instance.calculate_externalization_percentage(eec, tes), 2
            )

            user, percentage = user, externalization_percentage

            leaders.append({"user": User.objects.get(pk=user).full_name, "percentage": percentage})

        leaders_sorted = sorted(leaders, key=lambda leader: leader['percentage'], reverse=True)

        return Response(
            {
                "success": True,
                "leaders": leaders_sorted[:10],
                "organization_id": organization_id,
                "group": group.pk,
                "start_date": start_date,
                "end_date": end_date,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="organization_id",
                description="organization_id",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    @action(
        methods=['POST'],
        detail=False,
        permission_classes=[IsAdminOrUser],
        serializer_class=ExternalizationUpdaterSerializer,
        url_path="set-general-externalization-activities-score",
    )
    def set_general_activities_score_for_organization_externalization(self, request, pk=None):
        organization_id = request.query_params["organization_id"]
        organization = get_object_or_404(Organization, organization_id=organization_id)
        serializer = ExternalizationUpdaterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            externalization_instance = Externalization.objects.filter(organization=organization)
            externalization_instance.update(**serializer.validated_data)

            return Response(
                {
                    "success": True,
                    "data": ExternalizationSerializer(externalization_instance, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        permission_classes=[IsAdminOrUser],
        serializer_class=None,
    )
    def get_organization_combination_activity_scores(self, request, pk=None):
        """Get organization activity leaders for combination"""

        organization_id = request.query_params["organization_id"]
        group_pk = request.query_params["group_pk"]

        start_date = timezone.datetime.strptime(request.query_params["start_date"], "%Y-%m-%d")
        end_date = timezone.datetime.strptime(request.query_params["end_date"], "%Y-%m-%d")

        date_range = (start_date, end_date)

        try:
            group = Group.objects.get(pk=group_pk)
        except ObjectDoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': "group not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        users_in_group = UserGroup.objects.filter(groups=group.pk).values_list("user", flat=True)

        if not users_in_group:
            return Response(
                {
                    'success': True,
                    'message': f"{group.title} group has no member(s) attached",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        leaders = []
        for user in users_in_group:
            organization_activity_scores = self.get_organization_activity_scores(
                organization_id, group.pk, user, date_range
            )
            cec = organization_activity_scores["cec"]
            tes = organization_activity_scores["tes"]

            combination_instance = organization_activity_scores["combination_instance"]

            combination_percentage = round(
                combination_instance.calculate_combination_percentage(cec, tes), 2
            )

            user, percentage = user, combination_percentage

            leaders.append({"user": User.objects.get(pk=user).full_name, "percentage": percentage})

        leaders_sorted = sorted(leaders, key=lambda leader: leader['percentage'], reverse=True)

        return Response(
            {
                "success": True,
                "leaders": leaders_sorted[:10],
                "organization_id": organization_id,
                "group": group.pk,
                "start_date": start_date,
                "end_date": end_date,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="organization_id",
                description="organization_id",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    @action(
        methods=['POST'],
        detail=False,
        permission_classes=[IsAdminOrUser],
        serializer_class=CombinationUpdaterSerializer,
        url_path="set-general-combination-activities-score",
    )
    def set_general_activities_score_for_organization_combination(self, request, pk=None):
        organization_id = request.query_params["organization_id"]
        organization = get_object_or_404(Organization, organization_id=organization_id)
        serializer = CombinationUpdaterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            combination_instances = Combination.objects.filter(organization=organization)
            combination_instances.update(**serializer.validated_data)

            return Response(
                {
                    "success": True,
                    "data": CombinationSerializer(combination_instances, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        permission_classes=[IsAdminOrUser],
        serializer_class=None,
    )
    def get_organization_internalization_activity_scores(self, request, pk=None):
        """Get organization activity leaders for internalization"""

        organization_id = request.query_params["organization_id"]
        group_pk = request.query_params["group_pk"]

        start_date = timezone.datetime.strptime(request.query_params["start_date"], "%Y-%m-%d")
        end_date = timezone.datetime.strptime(request.query_params["end_date"], "%Y-%m-%d")

        date_range = (start_date, end_date)

        try:
            group = Group.objects.get(pk=group_pk)
        except ObjectDoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': "group not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        users_in_group = UserGroup.objects.filter(groups=group.pk).values_list("user", flat=True)

        if not users_in_group:
            return Response(
                {
                    'success': True,
                    'message': f"{group.title} group has no member(s) attached",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        leaders = []
        
        for user in users_in_group:
            organization_activity_scores = self.get_organization_activity_scores(
                organization_id, group.pk, user, date_range
            )
            iec = organization_activity_scores["iec"]
            tes = organization_activity_scores["tes"]

            internalization_instance = organization_activity_scores["internalization_instance"]
            internalization_percentage = round(
                internalization_instance.calculate_internalization_percentage(iec, tes), 2
            )

            user, percentage = user, internalization_percentage

            leaders.append({"user": User.objects.get(pk=user).full_name, "percentage": percentage})

        leaders_sorted = sorted(leaders, key=lambda leader: leader['percentage'], reverse=True)

        return Response(
            {
                "success": True,
                "leaders": leaders_sorted[:10],
                "organization_id": organization_id,
                "group": group,
                "start_date": start_date,
                "end_date": end_date,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="organization_id",
                description="organization_id",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    @action(
        methods=['POST'],
        detail=False,
        permission_classes=[IsAdminOrUser],
        serializer_class=InternalizationUpdaterSerializer,
        url_path="set-general-internalization-activities-score",
    )
    def set_general_activities_score_for_organization_externalization(self, request, pk=None):
        organization_id = request.query_params["organization_id"]
        organization = get_object_or_404(Organization, organization_id=organization_id)
        serializer = InternalizationUpdaterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            internalization_instances = Internalization.objects.filter(organization=organization)
            internalization_instances.update(**serializer.validated_data)

            return Response(
                {
                    "success": True,
                    "data": InternalizationSerializer(internalization_instances, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
