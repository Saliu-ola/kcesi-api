
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Activity_flag
from blog.models import  Blog
#from chat.models import chat-instance
from forum.models import Forum  
from .serializers import FlagSerializer, FlagStatusSerializer
from rest_framework.permissions import IsAuthenticated
from django.db import transaction




class FlagCreateView(generics.CreateAPIView):
    queryset = Activity_flag.objects.all()
    serializer_class = FlagSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context =  super().get_serializer_context()
        context['request_user'] = self.request.user
        return context

    def perform_create(self, serializer):
        serializer.save(flagged_by=self.request.user)


    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            activity_type_id = serializer.validated_data['activity_type_id']
            flagged_id = serializer.validated_data['flagged_id']

            flag_count = Activity_flag.objects.filter(activity_type_id=activity_type_id, flagged_id=flagged_id).count()
            still_active = True

            if activity_type_id == Activity_flag.BLOG and flag_count >= 3:
                still_active = False
                #Blog.objects.filter(id=flagged_id).update(active=False)

            elif activity_type_id == Activity_flag.FORUM and flag_count >= 3:
                still_active = False
                #Forum.objects.filter(id=flagged_id).update(active=False)

            elif activity_type_id == Activity_flag.CHAT and flag_count >= 1:
                still_active = False
                #Chat.objects.filter(id=flagged_id).update(active=False)

            return Response({'flagged count': flag_count, 'is_active':still_active, 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CheckFlagStatus(generics.CreateAPIView):
    queryset = Activity_flag.objects.all()
    serializer_class = FlagStatusSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            activity_type_id = serializer.validated_data['activity_type_id']
            flagged_id = serializer.validated_data['flagged_id']

            flag_count = Activity_flag.objects.filter(activity_type_id=activity_type_id, flagged_id=flagged_id).count()
            
            still_active = True

            if activity_type_id == Activity_flag.BLOG and flag_count >= 3:
                still_active = False

            elif activity_type_id == Activity_flag.FORUM and flag_count >= 3:
                still_active = False

            elif activity_type_id == Activity_flag.CHAT and flag_count >= 1:
                still_active = False

            return Response({'flagged count': flag_count, 'is_active':still_active, 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)