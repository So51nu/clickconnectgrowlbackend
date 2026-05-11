from rest_framework import serializers
from .models import HeaderMenu


class HeaderMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeaderMenu
        fields = [
            "id",
            "key",
            "title",
            "path",
            "match_type",
            "order",
            "is_active",
        ]