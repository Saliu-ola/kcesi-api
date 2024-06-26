from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import generics, status, viewsets, filters
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Token
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from organization.models import Organization
from accounts.permissions import IsAdmin, IsSuperAdmin, IsUser, IsSuperAdminOrAdmin, IsAdminOrUser
from .serializers import (
    UserSignUpSerializer,
    LoginUserSerializer,
    VerifyTokenSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    ListUserSerializer,
    OrganizationByNameInputSerializer,
    OrganizationByIDInputSerializer,
    UpdateUserImage,
)
from rest_framework.decorators import action
from django.db import transaction
from .tokens import create_jwt_pair_for_user
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from group.models import Group
from simpleblog.utils import calculate_engagement_scores
from blog.models import Blog, Comment
from in_app_chat.models import InAppChat
from resource.models import Resources
from browser_history.models import BrowserHistory
from forum.models import Forum
from topics.models import Topic
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import mixins
import cloudinary.uploader
from rest_framework.parsers import MultiPartParser, FormParser
from group.models import UserGroup
from group.serializers import GroupSerializer
from leader.models import Socialization, Externalization, Combination, Internalization
from simpleblog.utils import calculate_total_engagement_score
from .task import send_account_verification_mail, send_password_reset_mail
from datetime import datetime

# Create your views here.


class UserViewSets(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ListUserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'is_verified',
        'email',
        'organization_id',
        'first_group_id',
        'role_id',
        'phone',
        'organization_name',
        'gender',
        
    ]
    search_fields = [
        'email',
        'username',
        'phone',
        'organization_name',
        'first_name',
        'last_name',
    ]
    ordering_fields = ['created_at', 'last_login', 'email', 'role_id', 'first_group_id']

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [IsSuperAdminOrAdmin()]

        return super().get_permissions()

    def perform_destroy(self, instance):
        if instance.cloud_id is not None:
            cloudinary.uploader.destroy(instance.cloud_id)
        instance.delete()

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
        permission_classes=[IsAuthenticated],
        serializer_class=UpdateUserImage,
        url_path='update-user-image',
        parser_classes=[MultiPartParser],
    )
    def update_user_image(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data={"image": request.data["image"]})

        if serializer.is_valid():
            image = serializer.validated_data["image"]

            upload_result = cloudinary.uploader.upload(image, public_id=user.full_name)
            if "public_id" not in upload_result or "url" not in upload_result:
                return Response(
                    {"error": "Failed to upload image to Cloudinary"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            if user.cloud_id and user.image_url:
                cloudinary.uploader.destroy(user.cloud_id)

            user.cloud_id = upload_result["public_id"]
            user.image_url = upload_result["url"]
            user.save()

            return Response(
                {"success": True, "data": "User profle image udated successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="organization_name", description="organization_name", required=True, type=str
            ),
        ],
    )
    @action(
        methods=['GET'],
        detail=False,
        serializer_class=OrganizationByNameInputSerializer,
        url_path='get-organization-by-name',
    )
    def get_organization_by_name(self, request, pk=None):
        organization_name = request.query_params.get("organization_name")

        if not organization_name:
            return Response(
                {"error": "organization_name parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output = (
            User.objects.filter(organization_name=organization_name)
            .values('organization_id', 'organization_name')
            .first()
        )
        serializer = self.get_serializer(output)
        return Response(
            {"success": True, "data": serializer.data},
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
        responses={200: OrganizationByIDInputSerializer},
    )
    @action(
        methods=['GET'],
        detail=False,
        serializer_class=OrganizationByIDInputSerializer,
        url_path='get-organization-id',
    )
    def get_organization_by_id(self, request, pk=None):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        organization_id = serializer.validated_data["organization_id"]
        user = User.objects.filter(organization_id=organization_id).first()

        try:
            qs = UserGroup.objects.get(user=user).groups
            groups = GroupSerializer(instance=qs, many=True).data
        except ObjectDoesNotExist:
            groups = None

        context_data = {
            "organization_id": user.organization_id,
            "organization_name": user.organization_name,
            "groups": groups,
        }

        return Response(
            {"success": True, "data": OrganizationByIDInputSerializer(context_data).data},
            status=status.HTTP_200_OK,
        )

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
        url_path='get-total-members-by-organization',
    )
    def get_total_members_by_organization(self, request, pk=None):
        """Get total for an  organization members"""

        organization = request.query_params["organization"]
        organization_id = Organization.objects.get(pk=organization).organization_id
        output = User.objects.filter(organization_id=organization_id).count()

        if not output:
            return Response(
                {"success": False, "total_members": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_members": output},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-total-members',
    )
    def get_total_members(self, request, pk=None):
        """get total members in the app"""
        output = User.objects.count()
        if not output:
            return Response(
                {"success": False, "total_members": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_members": output},
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
        url_path='get-total-members-by-group',
    )
    def get_total_members_by_group(self, request, pk=None):
        """Get total for an  organization members by groups"""

        group = request.query_params["group"]

        output = UserGroup.objects.filter(groups=group).count()

        if not output:
            return Response(
                {"success": False, "total_members": 0},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": True, "total_members": output},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="group_id",
                description="group_id",
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
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-group-seci-details',
        permission_classes=[IsAdminOrUser],
    )
    def get_group_seci_details(self, request, pk=None):
        """Get seci detail"""

        group_id = request.query_params["group_id"]

        start_date = datetime.strptime(request.query_params["start_date"], "%Y-%m-%dT%H:%M:%S.%fZ")

        end_date = datetime.strptime(request.query_params["end_date"], "%Y-%m-%dT%H:%M:%S.%fZ")

        date_range = (start_date, end_date)

        try:
            group = Group.objects.get(pk=group_id)
        except ObjectDoesNotExist:
            return Response(
                {"message": f"Group {group_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        organization_id = group.organization_id
        try:
            organization = Organization.objects.get(organization_id=organization_id)
        except ObjectDoesNotExist:
            return Response(
                {"message": f"Organization with  {group.title} group not found or no longer exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            socialization_instance = Socialization.objects.get(
                organization=organization, group=group.pk
            )
        except ObjectDoesNotExist:
            return Response(
                {"message": f"Group {group.pk} have no socialization activities constants"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            externalization_instance = Externalization.objects.get(
                organization=organization, group=group.pk
            )
        except ObjectDoesNotExist:
            return Response(
                {"message": f"Group {group.pk} have no externalization activities constants"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            combination_instance = Combination.objects.get(
                organization=organization, group=group.pk
            )
        except ObjectDoesNotExist:
            return Response(
                {"message": f"Group {group.pk} have no combination activities constants"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            internalization_instance = Internalization.objects.get(
                organization=organization, group=group.pk
            )
        except ObjectDoesNotExist:
            return Response(
                {"message": f"Group {group.pk} have no internalization activities constants"},
                status=status.HTTP_404_NOT_FOUND,
            )

        post_blog = Blog.objects.filter(
            organization=organization, group=group.pk, created_at__range=date_range
        ).count()

        send_chat_message = InAppChat.objects.filter(
                organization=organization, group=group.pk, created_at__range=date_range
            ).count()

        post_forum = Forum.objects.filter(
            organization=organization, group=group.pk, created_at__range=date_range
        ).count()

        image_sharing = Resources.objects.filter(
            type='IMAGE',
            organization=organization,
            group=group.pk,
            created_at__range=date_range,
        ).count()

        video_sharing = Resources.objects.filter(
            type='VIDEO',
            organization=organization,
            group=group.pk,
            created_at__range=date_range,
        ).count()

        text_resource_sharing = Resources.objects.filter(
            type='DOCUMENT',
            organization=organization,
            group=group.pk,
            created_at__range=date_range,
        ).count()

        created_topic = Topic.objects.filter(
            organization=organization, group=group.pk, created_at__range=date_range
        ).count()

        comment = Comment.objects.filter(
                organization=organization, group=group.pk, created_at__range=date_range
            ).count()

        used_in_app_browser = BrowserHistory.objects.filter(
            organization=organization, group=group.pk, created_at__range=date_range
        ).count()

        recieve_chat_message = InAppChat.objects.filter(
            organization=organization, group=group.pk, created_at__range=date_range
        ).count()

        # Todo download_resource,read_blog,read_forum

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

        sec = socialization_instance.calculate_socialization_score(tallies)
        eec = externalization_instance.calculate_externalization_score(tallies)
        cec = combination_instance.calculate_combination_score(tallies)
        iec = internalization_instance.calculate_internalization_score(tallies)
        tes = calculate_total_engagement_score(sec, eec, cec, iec)

        socialization_percentage = round(
            socialization_instance.calculate_socialization_percentage(sec, tes), 2
        )

        externalization_percentage = round(
            externalization_instance.calculate_externalization_percentage(eec, tes), 2
        )

        combination_percentage = round(
            combination_instance.calculate_combination_percentage(cec, tes), 2
        )

        internalization_percentage = round(
            internalization_instance.calculate_internalization_percentage(iec, tes), 2
        )

        seci_details = {
            "socialization_engagement_score": sec,
            "externalization_engagement_score": eec,
            "combination_engagement_score": cec,
            "internalization_engagement_score": iec,
            "total_engagement_score": tes,
            "socialization_engagement_percentage": socialization_percentage,
            "externalization_engagement_percentage": externalization_percentage,
            "combination_engagement_percentage": combination_percentage,
            "internalization_engagement_percentage": internalization_percentage,
        }

        users_in_group = UserGroup.objects.filter(groups=group.pk).values_list("user", flat=True)

        return Response(
            {
                "success": True,
                "group": group_id,
                "seci_details": seci_details,
                "users_in_group": users_in_group,
                "start_date": start_date,
                "end_date": end_date,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="user_id",
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
        methods=['GET'],
        detail=False,
        serializer_class=None,
        url_path='get-user-seci-details',
        permission_classes=[IsAdminOrUser],
    )
    def get_user_seci_details(self, request, pk=None):
        """Get seci detail"""

        user_id = request.query_params["user_id"]

        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return Response(
                {"message": f"User {user_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            user_organization_pk = Organization.objects.get(organization_id=user.organization_id)
        except ObjectDoesNotExist:
            return Response(
                {"message": f"organization id - {user.organization_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        start_date = datetime.strptime(request.query_params["start_date"], "%Y-%m-%dT%H:%M:%S.%fZ")

        end_date = datetime.strptime(request.query_params["end_date"], "%Y-%m-%dT%H:%M:%S.%fZ")

        date_range = (start_date, end_date)

        user_groups = UserGroup.objects.filter(user=user).values_list("groups", flat=True)

        if not user_groups:
            return Response(
                {
                    "success": False,
                    "message": f"User {user.full_name}  with  id:- {user_id} does not belong to a group",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        sec_list = []
        eec_list = []
        cec_list = []
        iec_list = []

        for group in user_groups:

            try:
                socialization_instance = Socialization.objects.get(
                    group=group, organization=user_organization_pk
                )

            except ObjectDoesNotExist:
                return Response(
                    {
                        "message": f"User belongs to Group {group} which  have no socialization activities constants"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            try:
                externalization_instance = Externalization.objects.get(
                    group=group, organization=user_organization_pk
                )
            except ObjectDoesNotExist:
                return Response(
                    {
                        "message": f"User belongs to Group {group} which  have no externalization activities constants"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            try:
                combination_instance = Combination.objects.get(
                    group=group, organization=user_organization_pk
                )
            except ObjectDoesNotExist:
                return Response(
                    {
                        "message": f"User belongs to Group {group} which  have no combination activities constants"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            try:
                internalization_instance = Internalization.objects.get(
                    group=group, organization=user_organization_pk
                )
            except ObjectDoesNotExist:
                return Response(
                    {
                        "message": f"User belongs to Group {group} which  have no internalization activities constants"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            post_blog = Blog.objects.filter(author=user, created_at__range=date_range).count()

            send_chat_message = InAppChat.objects.filter(
                    sender=user, created_at__range=date_range
                ).count()

            post_forum = Forum.objects.filter(user=user, created_at__range=date_range).count()

            image_sharing = Resources.objects.filter(
                type='IMAGE',
                sender=user,
                created_at__range=date_range,
            ).count()

            video_sharing = Resources.objects.filter(
                    type='VIDEO',
                    sender=user,
                    created_at__range=date_range,
                ).count()

            text_resource_sharing = Resources.objects.filter(
                    type='DOCUMENT',
                    sender=user,
                    created_at__range=date_range,
                ).count()

            created_topic = Topic.objects.filter(
                    author=user, created_at__range=date_range
                ).count()

            comment = Comment.objects.filter(user=user, created_at__range=date_range).count()

            used_in_app_browser = BrowserHistory.objects.filter(
                    user=user, created_at__range=date_range
                ).count()

            recieve_chat_message = InAppChat.objects.filter(
                    receiver=user, created_at__range=date_range
                ).count()

            # # Todo download_resource,read_blog,read_forum

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

            sec = socialization_instance.calculate_socialization_score(tallies)
            eec = externalization_instance.calculate_externalization_score(tallies)
            cec = combination_instance.calculate_combination_score(tallies)
            iec = internalization_instance.calculate_internalization_score(tallies)

            sec_list.append(sec)
            eec_list.append(eec)
            cec_list.append(cec)
            iec_list.append(iec)

        sec_total = sum(sec_list)
        eec_total = sum(eec_list)
        cec_total = sum(cec_list)
        iec_total = sum(iec_list)

        tes = calculate_total_engagement_score(sec_total, eec_total, cec_total, iec_total)

        socialization_percentage = round(
            socialization_instance.calculate_socialization_percentage(sec_total, tes), 2
        )

        externalization_percentage = round(
            externalization_instance.calculate_externalization_percentage(eec_total, tes), 2
        )

        combination_percentage = round(
            combination_instance.calculate_combination_percentage(cec_total, tes), 2
        )

        internalization_percentage = round(
            internalization_instance.calculate_internalization_percentage(iec_total, tes), 2
        )

        seci_details = {
            "socialization_engagement_score": sec_total,
            "externalization_engagement_score": eec_total,
            "combination_engagement_score": cec_total,
            "internalization_engagement_score": iec_total,
            "total_engagement_score": tes,
            "socialization_engagement_percentage": socialization_percentage,
            "externalization_engagement_percentage": externalization_percentage,
            "combination_engagement_percentage": combination_percentage,
            "internalization_engagement_percentage": internalization_percentage,
        }

        return Response(
            {
                "success": True,
                "seci_details": seci_details,
                "user_groups": user_groups,
                "start_date": start_date,
                "end_date": end_date,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                'group', description='group', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                'organization_id',
                description='organization_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ]
    )
    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=ListUserSerializer,
        url_path='list-users-to-chat-with',
    )
    def get_list_of_users_to_chat_with(self, request, pk=None):
        group = request.query_params.get("group")
        organization_id = request.query_params.get("organization_id")

        if self.request.user.role_id == 1 and self.request.user.is_superuser:
            queryset = self.get_queryset()
            return Response(
                {
                    "success": True,
                    "count": queryset.count(),
                    "data": self.get_serializer(queryset, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            users_in_organization = self.get_queryset().filter(organization_id=organization_id)
            qs = users_in_organization

            if group is not None and group != '':
                users_in_group = UserGroup.objects.filter(
                    user__in=users_in_organization, groups=group
                ).values("user__pk")
                qs = self.get_queryset().filter(pk__in=users_in_group)

            return Response(
                {
                    "success": True,
                    "count": qs.count(),
                    "data": self.get_serializer(qs, many=True).data,
                },
                status=status.HTTP_200_OK,
            )


class UserSignUpView(generics.GenericAPIView):
    """Sign up endpoint"""

    serializer_class = UserSignUpSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request: Request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.update_or_create(
                user=user,
                token_type='ACCOUNT_VERIFICATION',
                defaults={'user': user, 'token_type': 'ACCOUNT_VERIFICATION'},
            )
            token.generate_random_token()

            verification_url = f"{settings.CLIENT_URL}/auth/verify_account/?token={token.token}"

            email_data = {
                "email": user.email,
                "full_name": user.full_name,
                "link": verification_url,
            }

            try:
                send_account_verification_mail(email_data)
            except Exception as e:
                # If an error occurs during email sending, rollback the transaction
                user.delete()
                return Response(data=str(e), status=status.HTTP_400_BAD_REQUEST)

            response = {"message": "User Created Successfully", "data": serializer.data}
            return Response(data=response, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyAccountView(generics.GenericAPIView):
    """Endpoint to verify the token and set user verified field to True"""

    permission_classes = [AllowAny]
    serializer_class = VerifyTokenSerializer

    def post(self, request: Request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            verification_token = Token.objects.filter(
                token=serializer.validated_data["token"]
            ).first()
            if verification_token:
                user = verification_token.user
                if user.is_verified:
                    return Response(
                        {"message": "Account is already verified"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    user.is_verified = True
                    user.save()
                    return Response(
                        {"message": "Account Verified Successfully"}, status=status.HTTP_200_OK
                    )
            else:
                return Response(
                    {'success': True, 'message': "Token not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = get_object_or_404(User, email=email)
            token, _ = Token.objects.update_or_create(
                user=user,
                token_type='PASSWORD_RESET',
                defaults={'user': user, 'token_type': 'PASSWORD_RESET'},
            )

            token.generate_random_token()
            reset_url = f"{settings.CLIENT_URL}/auth/password-reset/?token={token.token}"

            email_data = {
                "email": user.email,
                "full_name": user.full_name,
                "reset_link": reset_url,
            }

            send_password_reset_mail(email_data)

            return Response(
                {"message": "Password reset link sent successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data["new_password"]
            token = serializer.validated_data["token"]
            user_token = Token.objects.filter(token=token).first()
            if not user_token:
                return Response(
                    {"error": "token not found or Invalid token"}, status=status.HTTP_404_NOT_FOUND
                )
            user_token.reset_user_password(new_password)
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginUserSerializer

    def post(self, request: Request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            user = authenticate(email=email, password=password)

            if user is not None:
                if user.is_verified:
                    tokens = create_jwt_pair_for_user(user)

                    response = {
                        "message": "Login Successful",
                        "tokens": tokens,
                        **ListUserSerializer(instance=user).data,
                    }

                    return Response(data=response, status=status.HTTP_200_OK)
                else:
                    return Response(
                        data={"message": "User account not verified"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            else:
                return Response(
                    data={"message": "Invalid email or password"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
