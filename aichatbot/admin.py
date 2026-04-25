from django.contrib import admin
from .models import ChatbotTenant, ChatSession, ChatMessage, ChatLead


@admin.register(ChatbotTenant)
class ChatbotTenantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "website_url",
        "widget_key",
        "property_api_url",
        "bot_name",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "website_url",
        "widget_key",
        "admin_email",
        "property_api_url",
    )

    list_filter = ("is_active", "property_api_auth_type")

    readonly_fields = ("created_at",)

    fieldsets = (
        (
            "Tenant Basic Details",
            {
                "fields": (
                    "name",
                    "website_url",
                    "widget_key",
                    "logo_url",
                    "is_active",
                )
            },
        ),
        (
            "Property API Settings",
            {
                "fields": (
                    "property_api_url",
                    "property_api_auth_type",
                    "property_api_key_header",
                    "property_api_token",
                )
            },
        ),
        (
            "Chatbot Branding",
            {
                "fields": (
                    "primary_color",
                    "secondary_color",
                    "bot_name",
                    "welcome_message",
                    "fallback_message",
                )
            },
        ),
        (
            "Lead & Suggestions",
            {
                "fields": (
                    "admin_email",
                    "show_latest_projects_on_random_question",
                    "latest_project_limit",
                )
            },
        ),
        (
            "System",
            {
                "fields": ("created_at",)
            },
        ),
    )
class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("role", "message", "properties_payload", "created_at")
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = (
        "session_id",
        "tenant",
        "visitor_name",
        "visitor_phone",
        "source_url",
        "last_message_at",
    )
    search_fields = ("session_id", "visitor_name", "visitor_phone", "visitor_email")
    list_filter = ("tenant",)
    readonly_fields = ("created_at", "last_message_at")
    inlines = [ChatMessageInline]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "short_message", "created_at")
    search_fields = ("message", "session__session_id")
    list_filter = ("role", "created_at")

    def short_message(self, obj):
        return obj.message[:80]


@admin.register(ChatLead)
class ChatLeadAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "email",
        "property_title",
        "seller_name",
        "tenant",
        "created_at",
        "is_email_sent_to_admin",
        "is_email_sent_to_seller",
    )
    search_fields = ("name", "phone", "email", "property_title", "seller_name")
    list_filter = ("tenant", "is_email_sent_to_admin", "is_email_sent_to_seller")
    readonly_fields = ("created_at",)