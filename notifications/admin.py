from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification, UserNotification


def file_url(file_field):
    if not file_field:
        return ""
    try:
        return file_field.url
    except ValueError:
        return ""


def send_realtime_notification(user, notification, user_notification):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    unread_count = UserNotification.objects.filter(user=user, is_read=False, is_deleted=False).count()

    payload = {
        "type": "send_notification",
        "data": {
            "notification_id": notification.id,
            "user_notification_id": user_notification.id if user_notification else None,
            "title": notification.title,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "image": file_url(notification.image),
            "video": file_url(notification.video),
            "created_at": notification.created_at.isoformat(),
            "unread_count": unread_count,
        },
    }

    async_to_sync(channel_layer.group_send)(f"user_{user.id}", payload)


class NotificationAdminForm(forms.ModelForm):
    selected_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True).order_by("username"),
        required=False,
        label="Select Users",
        widget=FilteredSelectMultiple(verbose_name="Users", is_stacked=False),
        help_text=(
            "Leave blank to send this notification to ALL active users. "
            "Select specific users only when this notification should be visible to selected users."
        ),
    )

    class Meta:
        model = Notification
        fields = ["title", "message", "notification_type", "image", "video", "selected_users"]

    class Media:
        css = {"all": ("admin/css/widgets.css",)}
        js = (
            "admin/js/core.js",
            "admin/js/SelectBox.js",
            "admin/js/SelectFilter2.js",
        )


class UserNotificationInline(admin.TabularInline):
    model = UserNotification
    extra = 0
    can_delete = False
    readonly_fields = ["user", "is_read", "read_at", "is_deleted", "deleted_at", "delivered_at"]
    fields = ["user", "is_read", "read_at", "is_deleted", "deleted_at", "delivered_at"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationAdminForm

    list_display = [
        "id",
        "title",
        "notification_type",
        "created_by",
        "created_at",
        "audience_type",
        "has_image",
        "has_video",
        "total_users",
        "read_count",
        "unread_count",
        "deleted_count",
    ]

    search_fields = ["title", "message", "created_by__username", "created_by__email"]
    list_filter = ["notification_type", "created_at"]
    readonly_fields = [
        "created_by",
        "created_at",
        "audience_type",
        "total_users",
        "read_count",
        "unread_count",
        "deleted_count",
    ]
    inlines = [UserNotificationInline]

    fieldsets = (
        ("Notification Details", {
            "fields": (
                "title",
                "message",
                "notification_type",
                "image",
                "video",
                "selected_users",
            )
        }),
        ("Admin / Status", {
            "fields": (
                "created_by",
                "created_at",
                "audience_type",
                "total_users",
                "read_count",
                "unread_count",
                "deleted_count",
            ),
            "classes": ("collapse",),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            existing_user_ids = obj.user_statuses.values_list("user_id", flat=True)
            form.base_fields["selected_users"].initial = existing_user_ids
            form.base_fields["selected_users"].required = False
            form.base_fields["selected_users"].help_text = (
                "Leave blank to send/update this notification for ALL active users. "
                "Select users only for a selected-user notification."
            )
        return form

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

        selected_users = form.cleaned_data.get("selected_users")

        # Requirement: if no users are selected, send to every active user.
        if selected_users is None or not selected_users.exists():
            target_users = User.objects.filter(is_active=True).order_by("id")
        else:
            target_users = selected_users.filter(is_active=True).order_by("id")

        target_user_ids = set(target_users.values_list("id", flat=True))
        existing_user_ids = set(obj.user_statuses.values_list("user_id", flat=True))

        remove_user_ids = existing_user_ids - target_user_ids
        if remove_user_ids:
            UserNotification.objects.filter(notification=obj, user_id__in=remove_user_ids).delete()

        for user in target_users:
            user_notification, created = UserNotification.objects.get_or_create(
                notification=obj,
                user=user,
                defaults={"is_read": False},
            )
            if created:
                send_realtime_notification(user=user, notification=obj, user_notification=user_notification)

    def total_users(self, obj):
        return obj.user_statuses.count() if obj.pk else 0

    total_users.short_description = "Assigned Users"

    def read_count(self, obj):
        return obj.user_statuses.filter(is_read=True, is_deleted=False).count() if obj.pk else 0

    read_count.short_description = "Read"

    def unread_count(self, obj):
        return obj.user_statuses.filter(is_read=False, is_deleted=False).count() if obj.pk else 0

    unread_count.short_description = "Unread"

    def deleted_count(self, obj):
        return obj.user_statuses.filter(is_deleted=True).count() if obj.pk else 0

    deleted_count.short_description = "Deleted"

    def audience_type(self, obj):
        if not obj.pk:
            return "-"
        assigned_count = obj.user_statuses.count()
        total_active_users = User.objects.filter(is_active=True).count()
        if total_active_users > 0 and assigned_count >= total_active_users:
            return "All Users"
        return "Selected Users"

    audience_type.short_description = "Audience"

    def has_image(self, obj):
        return bool(obj.image)

    has_image.boolean = True
    has_image.short_description = "Image"

    def has_video(self, obj):
        return bool(obj.video)

    has_video.boolean = True
    has_video.short_description = "Video"


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "notification", "is_read", "read_at", "is_deleted", "deleted_at", "delivered_at"]
    search_fields = [
        "user__username",
        "user__email",
        "user__profile__full_name",
        "user__profile__phone",
        "user__login_profile__phone",
        "notification__title",
    ]
    list_filter = ["is_read", "is_deleted", "delivered_at", "notification__notification_type"]
    readonly_fields = ["notification", "user", "is_read", "read_at", "is_deleted", "deleted_at", "delivered_at"]

    def has_add_permission(self, request):
        return False
