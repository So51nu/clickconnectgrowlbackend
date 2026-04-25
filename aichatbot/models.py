from django.db import models


class ChatbotTenant(models.Model):
    name = models.CharField(max_length=150)
    website_url = models.URLField(blank=True, null=True)
    widget_key = models.CharField(max_length=120, unique=True)
    logo_url = models.URLField(blank=True, null=True)

    primary_color = models.CharField(max_length=20, default="#FF7A1A")
    secondary_color = models.CharField(max_length=20, default="#0B1320")
    bot_name = models.CharField(max_length=120, default="Property AI Assistant")

    welcome_message = models.TextField(
        default="Hi! Main aapki property search me help kar sakta hoon. Aap city, budget, BHK ya project name puch sakte ho."
    )
    fallback_message = models.TextField(
        default="Mujhe exact matching project nahi mila, lekin main aapko latest available projects suggest kar raha hoon."
    )
    property_api_url = models.URLField(
    blank=True,
    null=True,
    help_text="Tenant specific property/project API URL"
    )

    property_api_auth_type = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        choices=(
            ("none", "No Auth"),
            ("bearer", "Bearer Token"),
            ("api_key", "API Key Header"),
        ),
        default="none",
    )

    property_api_token = models.TextField(
        blank=True,
        null=True,
        help_text="Bearer token or API key if required"
    )

    property_api_key_header = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="Authorization",
        help_text="Example: Authorization or X-API-Key"
    )
    admin_email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    show_latest_projects_on_random_question = models.BooleanField(default=True)
    latest_project_limit = models.PositiveIntegerField(default=3)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ChatSession(models.Model):
    tenant = models.ForeignKey(
        ChatbotTenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_sessions",
    )
    session_id = models.CharField(max_length=180, db_index=True)
    visitor_name = models.CharField(max_length=120, blank=True, null=True)
    visitor_phone = models.CharField(max_length=30, blank=True, null=True)
    visitor_email = models.EmailField(blank=True, null=True)
    source_url = models.URLField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.session_id


class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("bot", "Bot"),
        ("system", "System"),
    )

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    message = models.TextField()
    properties_payload = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} - {self.session.session_id}"


class ChatLead(models.Model):
    tenant = models.ForeignKey(
        ChatbotTenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True, null=True)
    requirement = models.TextField(blank=True, null=True)

    property_id = models.PositiveIntegerField(blank=True, null=True)
    property_title = models.CharField(max_length=255, blank=True, null=True)
    seller_name = models.CharField(max_length=150, blank=True, null=True)
    seller_email = models.EmailField(blank=True, null=True)
    seller_phone = models.CharField(max_length=40, blank=True, null=True)

    source_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_email_sent_to_admin = models.BooleanField(default=False)
    is_email_sent_to_seller = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.phone}"