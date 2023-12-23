from rest_framework import serializers

from .models import BrowserHistory


class BrowserHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BrowserHistory
        fields = "__all__"
