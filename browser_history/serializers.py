from rest_framework import serializers

from .models import BrowserHistory


class BrowserHistorySerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source='user.full_name')

    class Meta:
        model = BrowserHistory
        fields = "__all__"
