from rest_framework import serializers
from .models import FooterSection, FooterMenuItem


class FooterMenuItemSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source="title", read_only=True)
    href = serializers.CharField(source="url", read_only=True)

    class Meta:
        model = FooterMenuItem
        fields = [
            "id",
            "title",
            "text",
            "url",
            "href",
            "order",
            "is_active",
            "is_login_modal",
        ]


class FooterSectionSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = FooterSection
        fields = [
            "id",
            "title",
            "slug",
            "section_type",
            "order",
            "is_active",
            "items",
        ]

    def get_items(self, obj):
        active_items = obj.items.filter(is_active=True).order_by("order", "id")
        return FooterMenuItemSerializer(active_items, many=True).data