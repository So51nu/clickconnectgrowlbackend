# from rest_framework import serializers
# from django.contrib.auth.models import User
# from users.models import UserLoginProfile, UserProfile
# from .models import Notification, UserNotification


# class NotificationUserSerializer(serializers.ModelSerializer):
#     full_name = serializers.SerializerMethodField()
#     phone = serializers.SerializerMethodField()
#     role = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = ["id", "username", "email", "full_name", "phone", "role"]

#     def get_full_name(self, obj):
#         if hasattr(obj, "profile"):
#             return obj.profile.full_name
#         return obj.get_full_name() or obj.username

#     def get_phone(self, obj):
#         if hasattr(obj, "login_profile"):
#             return obj.login_profile.phone
#         if hasattr(obj, "profile"):
#             return obj.profile.phone
#         return ""

#     def get_role(self, obj):
#         if hasattr(obj, "login_profile"):
#             return obj.login_profile.role
#         return ""


# class UserNotificationSerializer(serializers.ModelSerializer):
#     title = serializers.CharField(source="notification.title", read_only=True)
#     message = serializers.CharField(source="notification.message", read_only=True)
#     notification_type = serializers.CharField(source="notification.notification_type", read_only=True)
#     created_at = serializers.DateTimeField(source="notification.created_at", read_only=True)
#     created_by = serializers.SerializerMethodField()

#     class Meta:
#         model = UserNotification
#         fields = [
#             "id",
#             "title",
#             "message",
#             "notification_type",
#             "is_read",
#             "read_at",
#             "delivered_at",
#             "created_at",
#             "created_by",
#         ]

#     def get_created_by(self, obj):
#         user = obj.notification.created_by
#         if not user:
#             return None

#         return {
#             "id": user.id,
#             "username": user.username,
#             "email": user.email,
#         }


# class AdminNotificationCreateSerializer(serializers.Serializer):
#     title = serializers.CharField(max_length=255)
#     message = serializers.CharField()
#     notification_type = serializers.ChoiceField(
#         choices=Notification.NOTIFICATION_TYPE_CHOICES,
#         default="general"
#     )
#     user_ids = serializers.ListField(
#         child=serializers.IntegerField(),
#         allow_empty=False
#     )


# class AdminNotificationListSerializer(serializers.ModelSerializer):
#     total_users = serializers.SerializerMethodField()
#     read_count = serializers.SerializerMethodField()
#     unread_count = serializers.SerializerMethodField()
#     created_by_name = serializers.SerializerMethodField()

#     class Meta:
#         model = Notification
#         fields = [
#             "id",
#             "title",
#             "message",
#             "notification_type",
#             "created_at",
#             "created_by_name",
#             "total_users",
#             "read_count",
#             "unread_count",
#         ]

#     def get_total_users(self, obj):
#         return obj.user_statuses.count()

#     def get_read_count(self, obj):
#         return obj.user_statuses.filter(is_read=True).count()

#     def get_unread_count(self, obj):
#         return obj.user_statuses.filter(is_read=False).count()

#     def get_created_by_name(self, obj):
#         if obj.created_by:
#             return obj.created_by.username
#         return ""


# class AdminNotificationStatusSerializer(serializers.ModelSerializer):
#     user = NotificationUserSerializer(read_only=True)

#     class Meta:
#         model = UserNotification
#         fields = [
#             "id",
#             "user",
#             "is_read",
#             "read_at",
#             "delivered_at",
#         ]





from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import UserLoginProfile, UserProfile
from .models import Notification, UserNotification


class NotificationUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "full_name", "phone", "role"]

    def get_full_name(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.full_name
        return obj.get_full_name() or obj.username

    def get_phone(self, obj):
        if hasattr(obj, "login_profile"):
            return obj.login_profile.phone
        if hasattr(obj, "profile"):
            return obj.profile.phone
        return ""

    def get_role(self, obj):
        if hasattr(obj, "login_profile"):
            return obj.login_profile.role
        return ""


class UserNotificationSerializer(serializers.ModelSerializer):
    notification_id = serializers.IntegerField(source="notification.id", read_only=True)
    user_notification_id = serializers.IntegerField(source="id", read_only=True)
    title = serializers.CharField(source="notification.title", read_only=True)
    message = serializers.CharField(source="notification.message", read_only=True)
    notification_type = serializers.CharField(source="notification.notification_type", read_only=True)
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
            "is_read",
            "read_at",
            "delivered_at",
            "created_at",
            "created_by",
            "is_public",
            "recipient_count",
        ]

    def get_created_by(self, obj):
        user = obj.notification.created_by
        if not user:
            return None

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }

    def get_recipient_count(self, obj):
        return obj.notification.user_statuses.count()

    def get_is_public(self, obj):
        total_users = self.context.get("total_users") or User.objects.filter(is_active=True).count()
        recipient_count = obj.notification.user_statuses.count()
        return recipient_count == 0 or (total_users > 0 and recipient_count >= total_users)


class AdminNotificationCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    notification_type = serializers.ChoiceField(
        choices=Notification.NOTIFICATION_TYPE_CHOICES,
        default="general",
    )
    # Empty user_ids means public/general notification for everyone without login.
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list,
    )


class AdminNotificationListSerializer(serializers.ModelSerializer):
    total_users = serializers.SerializerMethodField()
    read_count = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    is_public = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "created_at",
            "created_by_name",
            "total_users",
            "read_count",
            "unread_count",
            "is_public",
        ]

    def get_total_users(self, obj):
        return obj.user_statuses.count()

    def get_read_count(self, obj):
        return obj.user_statuses.filter(is_read=True).count()

    def get_unread_count(self, obj):
        return obj.user_statuses.filter(is_read=False).count()

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.username
        return ""

    def get_is_public(self, obj):
        total_active_users = User.objects.filter(is_active=True).count()
        assigned_count = obj.user_statuses.count()
        return assigned_count == 0 or (total_active_users > 0 and assigned_count >= total_active_users)


class AdminNotificationStatusSerializer(serializers.ModelSerializer):
    user = NotificationUserSerializer(read_only=True)

    class Meta:
        model = UserNotification
        fields = [
            "id",
            "user",
            "is_read",
            "read_at",
            "delivered_at",
        ]
