
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
                # Update d blog instance
                #Blog.objects.filter(id=flagged_id).update(active=False)

            elif activity_type_id == Activity_flag.FORUM and flag_count >= 3:
                still_active = False
                # Update d actual forum instance
                #Forum.objects.filter(id=flagged_id).update(active=False)

            elif activity_type_id == Activity_flag.CHAT and flag_count >= 1:
                still_active = False
                # Update the actual chat instance
                #Chat.objects.filter(id=flagged_id).update(active=False)

            Activity_flag.objects.filter(activity_type_id=activity_type_id,
                                          flagged_id=flagged_id).update(flag_count=flag_count, active=still_active)


            # Update the serializer data
            updated_data = serializer.data.copy()
            updated_data['flag_count'] = flag_count
            updated_data['active'] = still_active

            return Response({'data':updated_data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







#Testing Purposes
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
    




#Alternative view Fks




# from rest_framework import generics, status
# from rest_framework.response import Response
# from .models import ActivityFlag
# from blog.models import Blog
# from forum.models import Forum
# from chat.models import ChatInstance
# from .serializers import FlagSerializer
# from rest_framework.permissions import IsAuthenticated
# from django.db import transaction

# class FlagActivityView(generics.CreateAPIView):
#     queryset = ActivityFlag.objects.all()
#     serializer_class = FlagSerializer
#     permission_classes = [IsAuthenticated]

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['request_user'] = self.request.user
#         return context

#     def perform_create(self, serializer):
#         serializer.save(flagged_by=self.request.user)

#     @transaction.atomic
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             self.perform_create(serializer)
#             activity_type = serializer.validated_data['activity_type']
#             flagged_instance = None

#             if activity_type == ActivityFlag.BLOG:
#                 flagged_instance = serializer.validated_data['blog']
#             elif activity_type == ActivityFlag.FORUM:
#                 flagged_instance = serializer.validated_data['forum']
#             elif activity_type == ActivityFlag.CHAT:
#                 flagged_instance = serializer.validated_data['chat']

#             if flagged_instance:
#                 flag_count = ActivityFlag.objects.filter(
#                     activity_type=activity_type,
#                     blog=flagged_instance if activity_type == ActivityFlag.BLOG else None,
#                     forum=flagged_instance if activity_type == ActivityFlag.FORUM else None,
#                     chat=flagged_instance if activity_type == ActivityFlag.CHAT else None
#                 ).count()

#                 still_active = True

#                 if activity_type in [ActivityFlag.BLOG, ActivityFlag.FORUM] and flag_count >= 3:
#                     still_active = False
#                     #flagged_instance.active = False
#                     flagged_instance.save()


#                 elif activity_type == ActivityFlag.CHAT and flag_count >= 1:
#                     still_active = False
#                     # flagged_instance.active = False
#                     flagged_instance.save()

             
#                 ActivityFlag.objects.filter(
#                     activity_type=activity_type,
#                     blog=flagged_instance if activity_type == ActivityFlag.BLOG else None,
#                     forum=flagged_instance if activity_type == ActivityFlag.FORUM else None,
#                     chat=flagged_instance if activity_type == ActivityFlag.CHAT else None
#                 ).update(flag_count=flag_count, active = still_active)

#                 updated_data = serializer.data.copy()
#                 updated_data['flag_count'] = flag_count
#                 updated_data['active'] = still_active

#                 return Response({'data':updated_data}, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
