from rest_framework import serializers
from .models import Activity_flag
from django.contrib.auth import get_user_model
from group.models import Group 
from .models import Activity_flag

User = get_user_model()


class CreateFlagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity_flag
        fields = ['activity_type_id', 'activity_id', 'flagged_by', 'author_id', 'group_id', 'comment', 'datetime_flagged', 'active', 'flag_count']
        read_only_fields = ['datetime_flagged', 'flagged_by', 'active', 'flag_count']




    def validate(self, data):
        request_user = self.context['request_user']
        if Activity_flag.objects.filter(activity_type_id=data['activity_type_id'],
                                         flagged_by=request_user, activity_id=data['activity_id']).exists():
            raise serializers.ValidationError("You have already flagged this content.")
        return data




act_type = {
    1:"Blog",
    2:"Chat",
    3:"Forum"
}



class FlagSerializer(serializers.ModelSerializer):
    flagged_by = serializers.CharField(source='flagged_by.username', read_only=True)
    author_name = serializers.SerializerMethodField()
    # group_id = serializers.SerializerMethodField()
    activity_type = serializers.SerializerMethodField()

    class Meta:
        model = Activity_flag
        fields = '__all__'

    def get_author_name(self, obj)-> str:
        return User.objects.get(pk=obj.author_id).username

    # def get_group_id(self, obj):
    #     return Group.objects.get(pk=obj.group_id).name

    def get_activity_type(self, obj)-> str:
        return act_type.get(obj.activity_type_id)



class DestroyFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity_flag
        fields = '__all__'



class FlagStatusSerializer(serializers.Serializer):
    activity_type_id = serializers.IntegerField(required=True)
    activity_id = serializers.IntegerField(required=True)











# #Alternative with FKs


# from rest_framework import serializers
# from .models import ActivityFlag
# from django.contrib.auth import get_user_model

# User = get_user_model()


# class FlagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ActivityFlag
#         fields = ['activity_type', 'blog', 'forum', 'chat', 'author_id', 'group_id',  'flagged_by', 'comment', 'datetime_flagged', 'active', 'flag_count']
#         read_only_fields = ['datetime_flagged', 'flagged_by', 'active', 'flag_count']


#     def validate(self, data):
#         request_user = self.context['request_user']
        
        
#         # I have to make sure only one activity field is returned
#         activity_fields = ['blog', 'forum', 'chat']
#         provided_activities = [data.get(field) for field in activity_fields if data.get(field) is not None]

#         if len(provided_activities) != 1:
#             raise serializers.ValidationError("Exactly one of 'blog', 'forum', or 'chat' must be provided.")
        
#         # This esures that d user hasn't flagged the content before

#         if ActivityFlag.objects.filter(
#                 activity_type=data['activity_type'],
#                 flagged_by=request_user,
#                 blog=data.get('blog'),
#                 forum=data.get('forum'),
#                 chat=data.get('chat')).exists():
#             raise serializers.ValidationError("You have already flagged this content.")
            
#         return data
