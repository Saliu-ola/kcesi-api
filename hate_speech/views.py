from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from .models import BadWord
from .serializers import (
  BadWordSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from accounts.permissions import IsAdmin, IsSuperAdmin, IsSuperAdminOrAdmin
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from organization.models import Organization


class BadWordsViewSets(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = BadWordSerializer
    permission_classes = [IsAuthenticated]
    queryset = BadWord.objects.all()

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=BadWordSerializer,
        url_path='add-words',
    )
    def add_words(self, request, pk=None):
        serializer = BadWordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            obj = self.get_queryset().first()
            new_words = serializer.validated_data["related_terms"]
            old_words = obj.related_terms
            merged_words = list(set(new_words + old_words))
            obj.related_terms = merged_words
            obj.save()

            return Response(status=200,data={"message":"words added successfully"})
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=BadWordSerializer,
        url_path='remove-words',
    )
    def remove_words(self, request, pk=None):
        serializer = BadWordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            obj = self.get_queryset().first()
            new_words = serializer.validated_data["related_terms"]
            old_words = obj.related_terms
            merged_words = [word for word in old_words if word not in new_words ]
            obj.related_terms = merged_words
            obj.save()

            return Response(status=200, data={"message": "words removed successfully"})
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
