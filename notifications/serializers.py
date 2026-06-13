from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Notification, UserNotification


def build_absolute_file_url(request, file_field):
    if not file_field:
        return ""

    try:
        url = file_field.url
    except ValueError:
        return ""

    if request:
        return request.build_absolute_uri(url)
    return url


class NotificationUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "full_name", "phone", "role"]

    def get_full_name(self, obj):
        if hasattr(obj, "profile") and getattr(obj.profile, "full_name", None):
            return obj.profile.full_name
        return obj.get_full_name() or obj.username

    def get_phone(self, obj):
        if hasattr(obj, "login_profile") and getattr(obj.login_profile, "phone", None):
            return obj.login_profile.phone
        if hasattr(obj, "profile") and getattr(obj.profile, "phone", None):
            return obj.profile.phone
        return ""

    def get_role(self, obj):
        if hasattr(obj, "login_profile") and getattr(obj.login_profile, "role", None):
            return obj.login_profile.role
        return ""


class UserNotificationSerializer(serializers.ModelSerializer):
    notification_id = serializers.IntegerField(source="notification.id", read_only=True)
    user_notification_id = serializers.IntegerField(source="id", read_only=True)
    title = serializers.CharField(source="notification.title", read_only=True)
    message = serializers.CharField(source="notification.message", read_only=True)
    notification_type = serializers.CharField(source="notification.notification_type", read_only=True)
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(source="notification.created_at", read_only=True)
    created_by = serializers.SerializerMethodField()
    is_public = serializers.SerializerMethodField()
    recipient_count = serializers.SerializerMethodField()

    class Meta:
        model = UserNotification
        fields = [
            "id",
            "notification_id",
            "user_notification_id",
            "title",
            "message",
            "notification_type",
            "image",
            "video",
            "is_read",
            "read_at",
            "is_deleted",
            "deleted_at",
            "delivered_at",
            "created_at",
            "created_by",
            "is_public",
            "recipient_count",
        ]

    def get_image(self, obj):
        return build_absolute_file_url(self.context.get("request"), obj.notification.image)

    def get_video(self, obj):
        return build_absolute_file_url(self.context.get("request"), obj.notification.video)

    def get_created_by(self, obj):
        user = obj.notification.created_by
        if not user:
            return None
        return {"id": user.id, "username": user.username, "email": user.email}

    def get_recipient_count(self, obj):
        return obj.notification.user_statuses.count()

    def get_is_public(self, obj):
        total_users = self.context.get("total_users") or User.objects.filter(is_active=True).count()
        recipient_count = obj.notification.user_statuses.count()
        return total_users > 0 and recipient_count >= total_users


class AdminNotificationCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    message = serializers.CharField(required=False, allow_blank=True, default="")
    notification_type = serializers.ChoiceField(
        choices=Notification.NOTIFICATION_TYPE_CHOICES,
        default="general",
    )
    image = serializers.FileField(required=False, allow_null=True)
    video = serializers.FileField(required=False, allow_null=True)

    # Blank / omitted user_ids = send to every active user.
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list,
    )


class AdminNotificationListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    total_users = serializers.SerializerMethodField()
    read_count = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    deleted_count = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    is_public = serializers.SerializerMethodField()
    audience_type = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "image",
            "video",
            "created_at",
            "created_by_name",
            "total_users",
            "read_count",
            "unread_count",
            "deleted_count",
            "is_public",
            "audience_type",
        ]

    def get_image(self, obj):
        return build_absolute_file_url(self.context.get("request"), obj.image)

    def get_video(self, obj):
        return build_absolute_file_url(self.context.get("request"), obj.video)

    def get_total_users(self, obj):
        return obj.user_statuses.count()

    def get_read_count(self, obj):
        return obj.user_statuses.filter(is_read=True, is_deleted=False).count()

    def get_unread_count(self, obj):
        return obj.user_statuses.filter(is_read=False, is_deleted=False).count()

    def get_deleted_count(self, obj):
        return obj.user_statuses.filter(is_deleted=True).count()

    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else ""

    def get_is_public(self, obj):
        total_active_users = User.objects.filter(is_active=True).count()
        assigned_count = obj.user_statuses.count()
        return total_active_users > 0 and assigned_count >= total_active_users

    def get_audience_type(self, obj):
        total_active_users = User.objects.filter(is_active=True).count()
        assigned_count = obj.user_statuses.count()
        if total_active_users > 0 and assigned_count >= total_active_users:
            return "All Users"
        return "Selected Users"


class AdminNotificationStatusSerializer(serializers.ModelSerializer):
    user = NotificationUserSerializer(read_only=True)

    class Meta:
        model = UserNotification
        fields = [
            "id",
            "user",
            "is_read",
            "read_at",
            "is_deleted",
            "deleted_at",
            "delivered_at",
        ]
