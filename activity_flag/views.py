
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Activity_flag
from blog.models import  Blog
#from chat.models import chat-instance
from forum.models import Forum  
from .serializers import FlagSerializer, FlagStatusSerializer, CreateFlagSerializer, DestroyFlagSerializer
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from group.models import Group
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound


User = get_user_model()



act_type = {
    1:"Blog",
    2:"Chat",
    3:"Forum"
}


class FlagCreateView(generics.ListCreateAPIView):
    queryset = Activity_flag.objects.all()
    serializer_class = CreateFlagSerializer
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
            activity_id = serializer.validated_data['activity_id']
            author_id = serializer.validated_data['author_id']
            group_id = serializer.validated_data['group_id']

            flag_count = Activity_flag.objects.filter(activity_type_id=activity_type_id, activity_id=activity_id).count()
            still_active = True

            if activity_type_id == Activity_flag.BLOG and flag_count >= 3:
                still_active = False
                # Update d blog instance
                #Blog.objects.filter(id=activity_id).update(active=False)

            elif activity_type_id == Activity_flag.FORUM and flag_count >= 3:
                still_active = False
                # Update d actual forum instance
                #Forum.objects.filter(id=activity_id).update(active=False)

            elif activity_type_id == Activity_flag.CHAT and flag_count >= 1:
                still_active = False
                # Update the actual chat instance
                #Chat.objects.filter(id=activity_id).update(active=False)

            Activity_flag.objects.filter(activity_type_id=activity_type_id,
                                          activity_id=activity_id).update(flag_count=flag_count, active=still_active)

            
            
            updated_data = serializer.data.copy()
            updated_data['author_id'] = User.objects.get(pk=author_id).username
            updated_data['flagged_by'] = request.user.username
            # updated_data['group_id'] =   Group.objects.get(pk=group_id).title
            updated_data['activity_type'] = act_type.get(activity_type_id)
            updated_data['flag_count'] = flag_count
            updated_data['active'] = still_active

            return Response({'data':updated_data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ActivityFlagListView(generics.ListAPIView):
    serializer_class = FlagSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Activity_flag.objects.all()
        group_id = self.request.query_params.get('group_id', None)
        if group_id is not None:
            queryset = queryset.filter(group_id=group_id)
            #  qurey by group using dis GET /list-flags/?group_id=1
        return queryset



class ActivityFlagRetrieveView(generics.RetrieveAPIView):
    queryset = Activity_flag.objects.all()
    serializer_class = FlagSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'



class ActivityFlagDeleteView(generics.DestroyAPIView):
    queryset = Activity_flag.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {"message": "Deleted successfully"}
        return Response(data=data,status=status.HTTP_200_OK)






    # def get_object(self):
    #     queryset = self.get_queryset()
    #     group_id = self.kwargs.get('group_id')
    #     activity_type_id = self.kwargs.get('activity_type_id')
    #     activity_id = self.kwargs.get('activity_id')
        

    #     try:
    #         obj = queryset.get(activity_id=activity_id, activity_type_id=activity_type_id, group_id=group_id)
    #     except Activity_flag.DoesNotExist:
    #         raise NotFound('Activity instance not found')

    #     return obj

    














#Testing Purposes
class CheckFlagStatus(generics.CreateAPIView):
    queryset = Activity_flag.objects.all()
    serializer_class = FlagStatusSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            activity_type_id = serializer.validated_data['activity_type_id']
            activity_id = serializer.validated_data['activity_id']

            flag_count = Activity_flag.objects.filter(activity_type_id=activity_type_id, activity_id=activity_id).count()
            
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
