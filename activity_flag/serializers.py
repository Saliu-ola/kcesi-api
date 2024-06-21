from rest_framework import serializers
from .models import Activity_flag
from django.contrib.auth import get_user_model

User = get_user_model()


class FlagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity_flag
        fields = ['activity_type_id', 'flagged_id', 'flagged_by', 'description', 'datetime_flagged']
        read_only_fields = ['datetime_flagged', 'flagged_by']


    def validate(self, data):
        request_user = self.context['request_user']
        if Activity_flag.objects.filter(activity_type_id=data['activity_type_id'],
                                         flagged_by=request_user, flagged_id=data['flagged_id']).exists():
            raise serializers.ValidationError("You have already flagged this content.")
        return data


class FlagStatusSerializer(serializers.Serializer):
    activity_type_id = serializers.IntegerField(required=True)
    flagged_id = serializers.IntegerField(required=True)