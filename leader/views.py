from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import AllowAny ,IsAuthenticated
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
from blog.models import Blog, Comment, BlogRead
from in_app_chat.models import InAppChat
from resource.models import Resources, ResourceDownload
from browser_history.models import BrowserHistory
from forum.models import Forum, ForumComment, ForumRead
from topics.models import Topic, BlogTopic, ForumTopic
from django.utils import timezone
from simpleblog.utils import (
    calculate_total_engagement_score,
    calculate_categorized_percentage,
    calculate_ai_division,
)
from accounts.models import User
from rest_framework.exceptions import ValidationError
from datetime import datetime
from decimal import Decimal
from django.db.models import Sum


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

    def get_aggregated_score(self, model, organization, group, date_range, kwargs):
        filters = {'organization': organization, 'group': group.pk, 'created_at__range': date_range}

        if kwargs:
            filters.update(**kwargs)
        aggregate_score = model.objects.filter(**filters).aggregate(total_score=Sum("score"))
        return aggregate_score.get("total_score") or 0.00

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


        post_blog_count = self.get_count_model_instances(
            Blog, organization, group, date_range, {'author': user}
        )
        print("post_blog_ai_count", post_blog_count,user)

        post_blog_ai_score = self.get_aggregated_score(
            Blog, organization, group, date_range, {'author': user}
        )
        # print("post_blog_ai_score", post_blog_ai_score,user)
        post_blog = post_blog_ai_score #calculate_ai_division(post_blog_ai_score, post_blog_count)
        # print("post_blog_ai_division", post_blog,user)

        send_chat_message_count = self.get_count_model_instances(
            InAppChat, organization, group, date_range, {'sender': user}
        )
        send_chat_message_ai_score = self.get_aggregated_score(
            InAppChat, organization, group, date_range, {'sender': user}
        )
        send_chat_message = send_chat_message_ai_score
        # send_chat_message = calculate_ai_division(
        #     send_chat_message_ai_score, send_chat_message_count
        # )

        post_forum_count = self.get_count_model_instances(
            Forum, organization, group, date_range, {'user': user}
        )
        post_forum_ai_score = self.get_aggregated_score(
            Forum, organization, group, date_range, {'user': user}
        )
        post_forum = post_forum_ai_score # calculate_ai_division(post_forum_ai_score , post_forum_count)


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
        
        # created_topic = self.get_count_model_instances(
        #     Topic, organization, group, date_range, {'author': user}
        # )

        created_blog_topic = self.get_count_model_instances(
            BlogTopic, organization, group, date_range, {'author': user}
        )

        created_forum_topic = self.get_count_model_instances(
            ForumTopic, organization, group, date_range, {'author': user}
        )

        created_topic = created_blog_topic + created_forum_topic

        comment_for_blog_count = self.get_count_model_instances(
            Comment,
            organization,
            group,
            date_range,
            {'user': user},
        )
        comment_for_forum_count = self.get_count_model_instances(
            ForumComment,
            organization,
            group,
            date_range,
            {'user': user},
        )

        total_comment_count = comment_for_blog_count + comment_for_forum_count

        comment_for_blog_ai_score = self.get_aggregated_score(
            Comment,
            organization,
            group,
            date_range,
            {'user': user},
        )
        comment_for_forum_ai_score = self.get_aggregated_score(
            ForumComment,
            organization,
            group,
            date_range,
            {'user': user},
        )

        total_comment_ai_score = Decimal(comment_for_blog_ai_score) + Decimal(comment_for_forum_ai_score)
        comment = total_comment_ai_score
        # comment = calculate_ai_division(total_comment_ai_score, total_comment_count)

        used_in_app_browser = BrowserHistory.objects.filter(
            organization=organization, group=group.pk, user = user, created_at__range=date_range
        ).aggregate(total_minutes=Sum('time_spent'))['total_minutes'] or 0

        used_in_app_browser = round(used_in_app_browser / 60, 2) 



        recieve_chat_message = self.get_count_model_instances(
            InAppChat,
            organization,
            group,
            date_range,
            {'receiver': user},
        )
        read_blog = self.get_count_model_instances(
            BlogRead,
            organization,
            group,
            date_range,
            {'user': user},
        )

        read_forum = self.get_count_model_instances(
            ForumRead,
            organization,
            group,
            date_range,
            {'user': user},
        )
        download_resources = self.get_count_model_instances(
            ResourceDownload,
            organization,
            group,
            date_range,
            {'user': user},
        )

        tallies = {
            "post_blog": post_blog,
            "send_chat_message": send_chat_message,
            "post_forum": post_forum,
            "image_sharing": image_sharing,
            "video_sharing": video_sharing,
            "text_resource_sharing": text_resource_sharing,
            # "created_topic": post_forum,
            "created_topic": created_topic,
            "comment": comment,
            "used_in_app_browser": used_in_app_browser,
            "read_blog": read_blog,
            "read_forum": read_forum,
            "recieve_chat_message": recieve_chat_message,
            "download_resources": download_resources,
        }
        print( tallies, user)

        socialization_instance = self.receive_model_instance(
            Socialization, organization_id, group, organization, "Socialization"
        )
        print("socialization_instance post_blog:", socialization_instance.post_blog)

        externalization_instance = self.receive_model_instance(
            Externalization, organization_id, group, organization, "Externalization"
        )

        internalization_instance = self.receive_model_instance(
            Internalization, organization_id, group, organization, "Internalization"
        )
        combination_instance = self.receive_model_instance(
            Combination, organization_id, group, organization, "Combination"
        )

        cec = combination_instance.calculate_combination_score(tallies)

        sec = socialization_instance.calculate_socialization_score(tallies)

        iec = internalization_instance.calculate_internalization_score(tallies)
        eec = externalization_instance.calculate_externalization_score(tallies)

        tes = calculate_total_engagement_score(sec, eec, cec, iec)


        return {
            "socialization_instance": socialization_instance,
            "externalization_instance": externalization_instance,
            "combination_instance": combination_instance,
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
                description="Start date in the format 'YYYY-MM-DD'T'HH:mm:ss.SSS'Z'",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="end_date",
                description="End date in the format 'YYYY-MM-DD'T'HH:mm:ss.SSS'Z'",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=None,
    )
    def get_organization_socialization_activity_scores(self, request, pk=None):
        """Get organization activity leaders for socialization"""

        organization_id = request.query_params["organization_id"]
        group_pk = request.query_params["group_pk"]

        start_date = datetime.strptime(request.query_params["start_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        end_date = datetime.strptime(request.query_params["end_date"], "%Y-%m-%dT%H:%M:%S.%fZ")

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
        # leaders = []
        user_sec_scores = [] 
        total_sec = Decimal(0.00)
        for user in users_in_group:
            organization_activity_scores = self.get_organization_activity_scores(
                organization_id, group.pk, user, date_range
            )

            sec = organization_activity_scores["sec"]
            tes = organization_activity_scores["tes"]

            # socialization_instance = organization_activity_scores["socialization_instance"]
            # my_percent = (sec/tes)*100
            # socialization_percentage = round(
            #     socialization_instance.calculate_socialization_percentage(sec, tes), 2
            # )

            total_sec += sec

            # user, percentage = user, socialization_percentage

            user_sec_scores.append({
                "user": User.objects.get(pk=user).full_name,
                "sec": sec,
                "tes": tes
            })


            # leaders.append({"user": User.objects.get(pk=user).full_name, "percentage": percentage})
        
        myleaders = []

        for score in user_sec_scores:
            percentage = (score['sec'] / total_sec) * 100 if total_sec > 0 else 0
            myleaders.append({
                "user": score['user'],
                "percentage": round(percentage, 2),
                "sec": score['sec']
            })
        

        # leaders_sorted = calculate_categorized_percentage(leaders)
        myleaders_sorted = sorted(myleaders, key=lambda x: x['percentage'], reverse=True)

        return Response(
            {
                "success": True,
                # "leaders": leaders_sorted[:5],
                "leaders": myleaders_sorted[:5],
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
        permission_classes=[IsAdminOrUser], ### Note!!!  y or user here
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
                description="Start date in the format 'YYYY-MM-DD'T'HH:mm:ss.SSS'Z'",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="end_date",
                description="End date in the format 'YYYY-MM-DD'T'HH:mm:ss.SSS'Z'",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=None,
    )
    def get_organization_externalization_activity_scores(self, request, pk=None):
        """Get organization activity leaders for externalization"""

        organization_id = request.query_params["organization_id"]
        group_pk = request.query_params["group_pk"]

        start_date = datetime.strptime(request.query_params["start_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        end_date = datetime.strptime(request.query_params["end_date"], "%Y-%m-%dT%H:%M:%S.%fZ")

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
        
        # leaders = []
        user_eec_scores = [] 
        total_eec = Decimal(0.00)
        for user in users_in_group:
            organization_activity_scores = self.get_organization_activity_scores(
                organization_id, group.pk, user, date_range
            )
            eec = organization_activity_scores["eec"]
            tes = organization_activity_scores["tes"]

            # externalization_instance = organization_activity_scores["externalization_instance"]
            # externalization_percentage = round(
            #     externalization_instance.calculate_externalization_percentage(eec, tes), 2
            # )
            
            total_eec += eec

            # user, percentage = user, externalization_percentage

            # leaders.append({"user": User.objects.get(pk=user).full_name, "percentage": percentage})

            user_eec_scores.append({
                "user": User.objects.get(pk=user).full_name,
                "eec": eec,
                "tes": tes
            })

        myleaders = []

        for score in user_eec_scores:
            percentage = (score['eec'] / total_eec) * 100 if total_eec > 0 else 0
            myleaders.append({
                "user": score['user'],
                "percentage": round(percentage, 2),
                "eec": score['eec']
            })
            

        # leaders_sorted = calculate_categorized_percentage(leaders)
        myleaders_sorted = sorted(myleaders, key=lambda x: x['percentage'], reverse=True)

        
        return Response(
            {
                "success": True,
                # "leaders": leaders_sorted[:5],
                "leaders": myleaders_sorted[:5],
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
                description="Start date in the format 'YYYY-MM-DD'T'HH:mm:ss.SSS'Z'",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="end_date",
                description="End date in the format 'YYYY-MM-DD'T'HH:mm:ss.SSS'Z'",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=None,
    )
    def get_organization_combination_activity_scores(self, request, pk=None):
        """Get organization activity leaders for combination"""

        organization_id = request.query_params["organization_id"]
        group_pk = request.query_params["group_pk"]

        start_date = datetime.strptime(request.query_params["start_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        end_date = datetime.strptime(request.query_params["end_date"], "%Y-%m-%dT%H:%M:%S.%fZ")

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
        
        # leaders = []
        user_cec_scores = [] 
        total_cec = Decimal(0.00)
        for user in users_in_group:
            organization_activity_scores = self.get_organization_activity_scores(
                organization_id, group.pk, user, date_range
            )
            cec = organization_activity_scores["cec"]
            tes = organization_activity_scores["tes"]

            # combination_instance = organization_activity_scores["combination_instance"]

            # combination_percentage = round(
            #     combination_instance.calculate_combination_percentage(cec, tes), 2
            # )
            total_cec += cec

            # user, percentage = user, combination_percentage

            user_cec_scores.append({
                "user": User.objects.get(pk=user).full_name,
                "cec": cec,
                "tes": tes
            })

            # leaders.append({"user": User.objects.get(pk=user).full_name, "percentage": percentage})

        myleaders = []

        for score in user_cec_scores:
            percentage = (score['cec'] / total_cec) * 100 if total_cec > 0 else 0
            myleaders.append({
                "user": score['user'],
                "percentage": round(percentage, 2),
                "cec": score['cec']
            })
        
        # leaders_sorted=calculate_categorized_percentage(leaders)
        myleaders_sorted = sorted(myleaders, key=lambda x: x['percentage'], reverse=True)


        return Response(
            {
                "success": True,
                # "leaders": leaders_sorted[:5],
                "leaders": myleaders_sorted[:5],
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
                description="Start date in the format 'YYYY-MM-DD'T'HH:mm:ss.SSS'Z'",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="end_date",
                description="End date in the format 'YYYY-MM-DD'T'HH:mm:ss.SSS'Z'",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=None,
    )
    def get_organization_internalization_activity_scores(self, request, pk=None):
        """Get organization activity leaders for internalization"""

        organization_id = request.query_params["organization_id"]
        group_pk = request.query_params["group_pk"]

        start_date = datetime.strptime(request.query_params["start_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        end_date = datetime.strptime(request.query_params["end_date"], "%Y-%m-%dT%H:%M:%S.%fZ")

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
        
        # leaders = []
        user_iec_scores = [] 
        total_iec = Decimal(0.00)
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

            total_iec += iec

            # user, percentage = user, internalization_percentage

            user_iec_scores.append({
                "user": User.objects.get(pk=user).full_name,
                "iec": iec,
                "tes": tes
            })

            # leaders.append({"user": User.objects.get(pk=user).full_name, "percentage": percentage})
        
        myleaders = []

        for score in user_iec_scores:
            percentage = (score['iec'] / total_iec) * 100 if total_iec > 0 else 0
            myleaders.append({
                "user": score['user'],
                "percentage": round(percentage, 2),
                "iec": score['iec']
            })

    
        # leaders_sorted = calculate_categorized_percentage(leaders)
        myleaders_sorted = sorted(myleaders, key=lambda x: x['percentage'], reverse=True)

        return Response(
            {
                "success": True,
                # "leaders": leaders_sorted[:5],
                "leaders": myleaders_sorted[:5],
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





#Attempt to optimse leaders view and avoid calling this function: get_organization_activity_scores() 4 different times
class SECIActivityLeadersView(APIView):
    permission_classes = [IsAuthenticated]

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
                description="Start date in the format 'YYYY-MM-DD'T'HH:mm:ss.SSS'Z'",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="end_date",
                description="End date in the format 'YYYY-MM-DD'T'HH:mm:ss.SSS'Z'",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    def get(self, request):
        organization_id = request.query_params["organization_id"]
        group_pk = request.query_params["group_pk"]

        start_date = datetime.strptime(request.query_params["start_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        end_date = datetime.strptime(request.query_params["end_date"], "%Y-%m-%dT%H:%M:%S.%fZ")

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

        socialization_leaders = []
        externalization_leaders = []
        combination_leaders = []
        internalization_leaders = []
        
        total_sec =  Decimal(0.00)
        total_eec =  Decimal(0.00)
        total_cec =  Decimal(0.00)
        total_iec =  Decimal(0.00)
        total_tes =  Decimal(0.00)

        user_sec_scores = [] 
        user_eec_scores = [] 
        user_cec_scores = [] 
        user_iec_scores = [] 

        for user in users_in_group:
            organization_activity_scores = self.get_organization_activity_scores(
                organization_id, group.pk, user, date_range
            )

            sec = organization_activity_scores["sec"]
            eec = organization_activity_scores["eec"]
            cec = organization_activity_scores["cec"]
            iec = organization_activity_scores["iec"]
            tes = organization_activity_scores["tes"]

            user_full_name = User.objects.get(pk=user).full_name

            total_sec += sec
            total_eec += eec
            total_cec += cec
            total_iec += iec
            total_tes += tes
            
            user_sec_scores.append({
                "user": user_full_name,
                "sec": sec,
                "tes": tes
            })

            user_eec_scores.append({
                "user": user_full_name,
                "eec": eec,
                "tes": tes
            })

            user_cec_scores.append({
                "user": user_full_name,
                "cec": cec,
                "tes": tes
            })

            user_iec_scores.append({
                "user": user_full_name,
                "iec": iec,
                "tes": tes
            })
        
        for score in user_sec_scores:
            percentage = (score['sec'] / total_sec) * 100 if total_sec > 0 else 0
            socialization_leaders.append({
                "user": score['user'],
                "percentage": round(percentage, 2),
                "sec": score['sec']
            }) 

        for score in user_eec_scores:
            percentage = (score['eec'] / total_eec) * 100 if total_eec > 0 else 0
            externalization_leaders.append({
                "user": score['user'],
                "percentage": round(percentage, 2),
                "eec": score['eec']
            })
            
        for score in user_cec_scores:
            percentage = (score['cec'] / total_cec) * 100 if total_cec > 0 else 0
            combination_leaders.append({
                "user": score['user'],
                "percentage": round(percentage, 2),
                "cec": score['cec']
            })

        for score in user_iec_scores:
            percentage = (score['iec'] / total_iec) * 100 if total_iec > 0 else 0
            internalization_leaders.append({
                "user": score['user'],
                "percentage": round(percentage, 2),
                "iec": score['iec']
            })
        
        socialization_leaders = sorted(socialization_leaders, key=lambda x: x['percentage'], reverse=True)
        externalization_leaders = sorted(externalization_leaders, key=lambda x: x['percentage'], reverse=True)
        combination_leaders = sorted(combination_leaders, key=lambda x: x['percentage'], reverse=True)
        internalization_leaders = sorted(internalization_leaders, key=lambda x: x['percentage'], reverse=True)

        return Response(
            {
                "success": True,
                "organization_id": organization_id,
                "group": group.pk,
                "start_date": start_date,
                "end_date": end_date,
                "socialization_leaders": socialization_leaders[:5],
                "externalization_leaders": externalization_leaders[:5],
                "combination_leaders": combination_leaders[:5],
                "internalization_leaders": internalization_leaders[:5],
            },
            status=status.HTTP_200_OK,
        )
    def get_organization_activity_scores(self, organization_id, group_pk, user, date_range):
        organization = get_object_or_404(Organization, organization_id=organization_id).pk
        group = get_object_or_404(Group, pk=group_pk)

        def get_aggregated_score(model, filters):
            aggregate_score = model.objects.filter(**filters).aggregate(total_score=Sum("score"))
            return aggregate_score.get("total_score") or 0.00

        def get_count_model_instances(model, filters):
            return model.objects.filter(**filters).count()

        base_filters = {'organization': organization, 'group': group.pk, 'created_at__range': date_range}

        # Calculate scores and counts
        post_blog_count = get_count_model_instances(Blog, {**base_filters, 'author': user})
        post_blog_ai_score = get_aggregated_score(Blog, {**base_filters, 'author': user})
        post_blog = calculate_ai_division(post_blog_ai_score, post_blog_count)

        send_chat_message_count = get_count_model_instances(InAppChat, {**base_filters, 'sender': user})
        send_chat_message_ai_score = get_aggregated_score(InAppChat, {**base_filters, 'sender': user})
        send_chat_message = calculate_ai_division(send_chat_message_ai_score, send_chat_message_count)

        post_forum_count = get_count_model_instances(Forum, {**base_filters, 'user': user})
        post_forum_ai_score = get_aggregated_score(Forum, {**base_filters, 'user': user})
        post_forum = calculate_ai_division(post_forum_ai_score, post_forum_count)

        image_sharing = get_count_model_instances(Resources, {**base_filters, 'type': 'IMAGE', 'sender': user})
        video_sharing = get_count_model_instances(Resources, {**base_filters, 'type': 'VIDEO', 'sender': user})
        text_resource_sharing = get_count_model_instances(Resources, {**base_filters, 'type': 'DOCUMENT', 'sender': user})

        created_blog_topic = get_count_model_instances(BlogTopic, {**base_filters, 'author': user})
        created_forum_topic = get_count_model_instances(ForumTopic, {**base_filters, 'author': user})
        created_topic = created_blog_topic + created_forum_topic

        comment_for_blog_count = get_count_model_instances(Comment, {**base_filters, 'user': user})
        comment_for_forum_count = get_count_model_instances(ForumComment, {**base_filters, 'user': user})
        total_comment_count = comment_for_blog_count + comment_for_forum_count

        comment_for_blog_ai_score = get_aggregated_score(Comment, {**base_filters, 'user': user})
        comment_for_forum_ai_score = get_aggregated_score(ForumComment, {**base_filters, 'user': user})
        total_comment_ai_score = Decimal(comment_for_blog_ai_score) + Decimal(comment_for_forum_ai_score)
        comment = calculate_ai_division(total_comment_ai_score, total_comment_count)

        used_in_app_browser = BrowserHistory.objects.filter(**base_filters, user=user).aggregate(total_minutes=Sum('time_spent'))['total_minutes'] or 0
        used_in_app_browser = round(used_in_app_browser / 60, 2)

        recieve_chat_message = get_count_model_instances(InAppChat, {**base_filters, 'receiver': user})
        read_blog = get_count_model_instances(BlogRead, {**base_filters, 'user': user})
        read_forum = get_count_model_instances(ForumRead, {**base_filters, 'user': user})
        download_resources = get_count_model_instances(ResourceDownload, {**base_filters, 'user': user})

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
            "read_blog": read_blog,
            "read_forum": read_forum,
            "recieve_chat_message": recieve_chat_message,
            "download_resources": download_resources,
        }

        socialization_instance = get_object_or_404(Socialization, organization=organization, group=group.pk)
        externalization_instance = get_object_or_404(Externalization, organization=organization, group=group.pk)
        internalization_instance = get_object_or_404(Internalization, organization=organization, group=group.pk)
        combination_instance = get_object_or_404(Combination, organization=organization, group=group.pk)

        cec = combination_instance.calculate_combination_score(tallies)
        sec = socialization_instance.calculate_socialization_score(tallies)
        iec = internalization_instance.calculate_internalization_score(tallies)
        eec = externalization_instance.calculate_externalization_score(tallies)

        tes = calculate_total_engagement_score(sec, eec, cec, iec)

        return {
            "socialization_instance": socialization_instance,
            "externalization_instance": externalization_instance,
            "combination_instance": combination_instance,
            "internalization_instance": internalization_instance,
            "tes": tes,
            "sec": sec,
            "eec": eec,
            "cec": cec,
            "iec": iec,
        }

        