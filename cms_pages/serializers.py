from rest_framework import serializers

from .models import CMSPage, clean_html_content


class CMSPagePublicSerializer(serializers.ModelSerializer):
    page_url = serializers.SerializerMethodField()

    class Meta:
        model = CMSPage
        fields = [
            "id",
            "title",
            "slug",
            "page_url",
            "html_content",
            "meta_title",
            "meta_description",
            "meta_keywords",
            "updated_at",
        ]

    def get_page_url(self, obj):
        return f"/cms-pages/{obj.slug}"


class CMSPageAdminSerializer(serializers.ModelSerializer):
    page_url = serializers.SerializerMethodField()

    class Meta:
        model = CMSPage
        fields = [
            "id",
            "title",
            "slug",
            "page_url",
            "html_content",
            "meta_title",
            "meta_description",
            "meta_keywords",
            "status",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "page_url"]

    def get_page_url(self, obj):
        return f"/cms-pages/{obj.slug}"

    def validate_html_content(self, value):
        return clean_html_content(value)
