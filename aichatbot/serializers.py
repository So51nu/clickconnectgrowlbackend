from rest_framework import serializers
from .models import ChatbotTenant, ChatLead


class ChatbotTenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotTenant
        fields = (
            "name",
            "website_url",
            "widget_key",
            "logo_url",
            "primary_color",
            "secondary_color",
            "bot_name",
            "welcome_message",
            "fallback_message",
            "show_latest_projects_on_random_question",
            "latest_project_limit",
        )


class ChatLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatLead
        fields = "__all__"
        read_only_fields = (
            "tenant",
            "session",
            "property_title",
            "seller_name",
            "seller_email",
            "seller_phone",
            "is_email_sent_to_admin",
            "is_email_sent_to_seller",
        )