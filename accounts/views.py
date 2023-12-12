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
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)

from .serializers import (
    SignUpSerializer,
    LoginUserSerializer,
    VerifyTokenSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    ListUserSerializer,
)
from .tokens import create_jwt_pair_for_user

# Create your views here.


class SignUpView(generics.GenericAPIView):
    """Sign up endpoint"""

    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

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

            # user_data = {'id': user.id, 'email': user.email, 'username': f"{user.username}",
            #          'url': verification_url} will be done with celery and proper email content

            # Send email with verification link
            send_mail(
                'Verify Your Account',
                f'Click the following link to verify your account: {verification_url}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

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
                        "email": email,
                        "role": user.role_id,
                        "organization_id": user.organization_id,
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

            # Send email with password reset link
            send_mail(
                'Password Reset',
                f'Click the following link to reset your password: {reset_url}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

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


class UserViewSets(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "put", "delete"]
    serializer_class = ListUserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'is_verified',
        'email',
        'organization_id',
        'group_id',
        'role_id',
        'phone',
    ]
    search_fields = ['email', 'username', 'phone', 'organization_name']
    ordering_fields = ['created_at', 'last_login', 'email', 'role_id', 'group_id']

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'destroy']:
            return [IsAdminUser()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated()]
        else:
            return [AllowAny()]

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
