# from django import forms
# from django.contrib import admin
# from django.contrib.auth.models import User
# from django.contrib.admin.widgets import FilteredSelectMultiple

# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer

# from .models import Notification, UserNotification


# def send_realtime_notification(user, notification, user_notification):
#     """
#     Django Admin se notification save hote hi selected user ko realtime WebSocket send karega.
#     """
#     channel_layer = get_channel_layer()

#     if not channel_layer:
#         return

#     unread_count = UserNotification.objects.filter(
#         user=user,
#         is_read=False
#     ).count()

#     payload = {
#         "type": "send_notification",
#         "data": {
#             "notification_id": notification.id,
#             "user_notification_id": user_notification.id,
#             "title": notification.title,
#             "message": notification.message,
#             "notification_type": notification.notification_type,
#             "created_at": notification.created_at.isoformat(),
#             "unread_count": unread_count,
#         }
#     }

#     async_to_sync(channel_layer.group_send)(
#         f"user_{user.id}",
#         payload
#     )


# class NotificationAdminForm(forms.ModelForm):
#     selected_users = forms.ModelMultipleChoiceField(
#         queryset=User.objects.filter(is_active=True).order_by("username"),
#         required=True,
#         label="Select Users",
#         widget=FilteredSelectMultiple(
#             verbose_name="Users",
#             is_stacked=False
#         ),
#         help_text="Select one or multiple users to send this notification."
#     )

#     class Meta:
#         model = Notification
#         fields = [
#             "title",
#             "message",
#             "notification_type",
#             "selected_users",
#         ]

#     class Media:
#         css = {
#             "all": ("admin/css/widgets.css",)
#         }
#         js = (
#             "admin/js/core.js",
#             "admin/js/SelectBox.js",
#             "admin/js/SelectFilter2.js",
#         )


# class UserNotificationInline(admin.TabularInline):
#     model = UserNotification
#     extra = 0
#     can_delete = False
#     readonly_fields = [
#         "user",
#         "is_read",
#         "read_at",
#         "delivered_at",
#     ]

#     fields = [
#         "user",
#         "is_read",
#         "read_at",
#         "delivered_at",
#     ]

#     def has_add_permission(self, request, obj=None):
#         return False


# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     form = NotificationAdminForm

#     list_display = [
#         "id",
#         "title",
#         "notification_type",
#         "created_by",
#         "created_at",
#         "total_users",
#         "read_count",
#         "unread_count",
#     ]

#     search_fields = [
#         "title",
#         "message",
#         "created_by__username",
#         "created_by__email",
#     ]

#     list_filter = [
#         "notification_type",
#         "created_at",
#     ]

#     readonly_fields = [
#         "created_by",
#         "created_at",
#         "total_users",
#         "read_count",
#         "unread_count",
#     ]

#     inlines = [UserNotificationInline]

#     fieldsets = (
#         ("Notification Details", {
#             "fields": (
#                 "title",
#                 "message",
#                 "notification_type",
#                 "selected_users",
#             )
#         }),
#         ("Admin / Status", {
#             "fields": (
#                 "created_by",
#                 "created_at",
#                 "total_users",
#                 "read_count",
#                 "unread_count",
#             ),
#             "classes": ("collapse",),
#         }),
#     )

#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)

#         if obj:
#             existing_user_ids = obj.user_statuses.values_list("user_id", flat=True)
#             form.base_fields["selected_users"].initial = existing_user_ids
#             form.base_fields["selected_users"].required = False
#             form.base_fields["selected_users"].help_text = (
#                 "Existing users are already selected. Add more users if you want to send this notification to new users also."
#             )

#         return form

#     def save_model(self, request, obj, form, change):
#         if not obj.created_by:
#             obj.created_by = request.user

#         super().save_model(request, obj, form, change)

#         selected_users = form.cleaned_data.get("selected_users")

#         if not selected_users:
#             return

#         for user in selected_users:
#             user_notification, created = UserNotification.objects.get_or_create(
#                 notification=obj,
#                 user=user,
#                 defaults={
#                     "is_read": False,
#                 }
#             )

#             # New notification create hone par ya new user add hone par realtime send hoga.
#             if created:
#                 send_realtime_notification(
#                     user=user,
#                     notification=obj,
#                     user_notification=user_notification
#                 )

#     def total_users(self, obj):
#         if not obj.pk:
#             return 0
#         return obj.user_statuses.count()

#     total_users.short_description = "Total Users"

#     def read_count(self, obj):
#         if not obj.pk:
#             return 0
#         return obj.user_statuses.filter(is_read=True).count()

#     read_count.short_description = "Read"

#     def unread_count(self, obj):
#         if not obj.pk:
#             return 0
#         return obj.user_statuses.filter(is_read=False).count()

#     unread_count.short_description = "Unread"


# @admin.register(UserNotification)
# class UserNotificationAdmin(admin.ModelAdmin):
#     list_display = [
#         "id",
#         "user",
#         "notification",
#         "is_read",
#         "read_at",
#         "delivered_at",
#     ]

#     search_fields = [
#         "user__username",
#         "user__email",
#         "user__profile__full_name",
#         "user__profile__phone",
#         "user__login_profile__phone",
#         "notification__title",
#     ]

#     list_filter = [
#         "is_read",
#         "delivered_at",
#         "notification__notification_type",
#     ]

#     readonly_fields = [
#         "notification",
#         "user",
#         "is_read",
#         "read_at",
#         "delivered_at",
#     ]

#     def has_add_permission(self, request):
#         return False




from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification, UserNotification


def send_realtime_notification(user, notification, user_notification):
    """
    Django Admin se selected user ko realtime WebSocket send karega.
    Public/general notification users ko API polling se show hogi.
    """
    channel_layer = get_channel_layer()

    if not channel_layer:
        return

    unread_count = UserNotification.objects.filter(
        user=user,
        is_read=False,
    ).count()

    payload = {
        "type": "send_notification",
        "data": {
            "notification_id": notification.id,
            "user_notification_id": user_notification.id if user_notification else None,
            "title": notification.title,
            "message": notification.message,
            "notification_type": notification.notification_type,
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
        widget=FilteredSelectMultiple(
            verbose_name="Users",
            is_stacked=False,
        ),
        help_text=(
            "Leave blank to create a public/general notification visible to everyone without login. "
            "Select users for assigned notifications. Select all active users if this should also be treated as everyone notification."
        ),
    )

    class Meta:
        model = Notification
        fields = [
            "title",
            "message",
            "notification_type",
            "selected_users",
        ]

    class Media:
        css = {
            "all": ("admin/css/widgets.css",)
        }
        js = (
            "admin/js/core.js",
            "admin/js/SelectBox.js",
            "admin/js/SelectFilter2.js",
        )


class UserNotificationInline(admin.TabularInline):
    model = UserNotification
    extra = 0
    can_delete = False
    readonly_fields = [
        "user",
        "is_read",
        "read_at",
        "delivered_at",
    ]

    fields = [
        "user",
        "is_read",
        "read_at",
        "delivered_at",
    ]

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
        "total_users",
        "read_count",
        "unread_count",
    ]

    search_fields = [
        "title",
        "message",
        "created_by__username",
        "created_by__email",
    ]

    list_filter = [
        "notification_type",
        "created_at",
    ]

    readonly_fields = [
        "created_by",
        "created_at",
        "audience_type",
        "total_users",
        "read_count",
        "unread_count",
    ]

    inlines = [UserNotificationInline]

    fieldsets = (
        ("Notification Details", {
            "fields": (
                "title",
                "message",
                "notification_type",
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
                "Leave blank for public/general notification. Existing selected users are prefilled."
            )

        return form

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user

        super().save_model(request, obj, form, change)

        selected_users = form.cleaned_data.get("selected_users")

        # Blank selected_users = public/general notification. No UserNotification rows needed.
        if selected_users is None:
            return

        existing_user_ids = set(obj.user_statuses.values_list("user_id", flat=True))
        selected_user_ids = set(selected_users.values_list("id", flat=True))

        # If admin removed users while editing, remove their assignment rows.
        remove_user_ids = existing_user_ids - selected_user_ids
        if remove_user_ids:
            UserNotification.objects.filter(notification=obj, user_id__in=remove_user_ids).delete()

        for user in selected_users:
            user_notification, created = UserNotification.objects.get_or_create(
                notification=obj,
                user=user,
                defaults={"is_read": False},
            )

            if created:
                send_realtime_notification(
                    user=user,
                    notification=obj,
                    user_notification=user_notification,
                )

    def total_users(self, obj):
        if not obj.pk:
            return 0
        return obj.user_statuses.count()

    total_users.short_description = "Assigned Users"

    def read_count(self, obj):
        if not obj.pk:
            return 0
        return obj.user_statuses.filter(is_read=True).count()

    read_count.short_description = "Read"

    def unread_count(self, obj):
        if not obj.pk:
            return 0
        return obj.user_statuses.filter(is_read=False).count()

    unread_count.short_description = "Unread"

    def audience_type(self, obj):
        if not obj.pk:
            return "-"

        assigned_count = obj.user_statuses.count()
        total_active_users = User.objects.filter(is_active=True).count()

        if assigned_count == 0:
            return "Public / General"

        if total_active_users > 0 and assigned_count >= total_active_users:
            return "All Users"

        return "Selected Users"

    audience_type.short_description = "Audience"


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "notification",
        "is_read",
        "read_at",
        "delivered_at",
    ]

    search_fields = [
        "user__username",
        "user__email",
        "user__profile__full_name",
        "user__profile__phone",
        "user__login_profile__phone",
        "notification__title",
    ]

    list_filter = [
        "is_read",
        "delivered_at",
        "notification__notification_type",
    ]

    readonly_fields = [
        "notification",
        "user",
        "is_read",
        "read_at",
        "delivered_at",
    ]

    def has_add_permission(self, request):
        return False
