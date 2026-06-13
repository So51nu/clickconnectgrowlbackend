from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .authentication import BearerTokenAuthentication
from .models import Notification, UserNotification
from .serializers import (
    NotificationUserSerializer,
    AdminNotificationCreateSerializer,
    AdminNotificationListSerializer,
    AdminNotificationStatusSerializer,
    build_absolute_file_url,
)


class IsAdminUserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


def get_total_active_users():
    return User.objects.filter(is_active=True).count()


def all_active_users_queryset():
    return User.objects.filter(is_active=True).order_by("id")


def public_notification_filter(total_users):
    """
    Guest users can see notifications that were sent to all active users.
    recipient_count=0 is kept for very old notifications created before this module
    started creating UserNotification rows.
    """
    query = Q(recipient_count=0)
    if total_users > 0:
        query = query | Q(recipient_count__gte=total_users)
    return query


def get_user_status_map(notification_ids, user):
    if not user or not user.is_authenticated or not notification_ids:
        return {}

    statuses = UserNotification.objects.filter(
        user=user,
        notification_id__in=notification_ids,
    ).select_related("notification")

    return {status.notification_id: status for status in statuses}


def serialize_notification(request, notification, user_status=None, total_users=0):
    recipient_count = getattr(notification, "recipient_count", None)
    if recipient_count is None:
        recipient_count = notification.user_statuses.count()

    is_public = recipient_count == 0 or (total_users > 0 and recipient_count >= total_users)

    created_by = None
    if notification.created_by:
        created_by = {
            "id": notification.created_by.id,
            "username": notification.created_by.username,
            "email": notification.created_by.email,
        }

    return {
        # id is user notification id for assigned notifications, notification id for old public notifications.
        "id": user_status.id if user_status else notification.id,
        "notification_id": notification.id,
        "user_notification_id": user_status.id if user_status else None,
        "title": notification.title,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "image": build_absolute_file_url(request, notification.image),
        "video": build_absolute_file_url(request, notification.video),
        "is_read": bool(user_status.is_read) if user_status else False,
        "read_at": user_status.read_at if user_status else None,
        "is_deleted": bool(user_status.is_deleted) if user_status else False,
        "deleted_at": user_status.deleted_at if user_status else None,
        "delivered_at": user_status.delivered_at if user_status else notification.created_at,
        "created_at": notification.created_at,
        "created_by": created_by,
        "is_public": is_public,
        "recipient_count": recipient_count,
    }


def file_url(file_field):
    if not file_field:
        return ""
    try:
        return file_field.url
    except ValueError:
        return ""


def get_user_unread_count(user):
    return UserNotification.objects.filter(user=user, is_read=False, is_deleted=False).count()


def send_realtime_notification_to_user(user, notification, user_notification):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    unread_count = get_user_unread_count(user)

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


def get_target_users_from_user_ids(user_ids):
    # Requirement: if no users selected, send to all active users.
    if not user_ids:
        return all_active_users_queryset(), True
    return User.objects.filter(id__in=user_ids, is_active=True).distinct().order_by("id"), False


class AdminSearchUsersAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
    permission_classes = [IsAdminUserOnly]

    def get(self, request):
        search = request.GET.get("search", "").strip()
        role = request.GET.get("role", "").strip()

        users = User.objects.all().order_by("-id")

        if search:
            users = users.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(profile__full_name__icontains=search)
                | Q(profile__phone__icontains=search)
                | Q(login_profile__phone__icontains=search)
            )

        if role:
            users = users.filter(login_profile__role=role)

        users = users.distinct()[:50]
        serializer = NotificationUserSerializer(users, many=True)
        return Response({"success": True, "users": serializer.data})


class AdminCreateNotificationAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
    permission_classes = [IsAdminUserOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        serializer = AdminNotificationCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        title = serializer.validated_data["title"]
        message = serializer.validated_data.get("message", "")
        notification_type = serializer.validated_data["notification_type"]
        user_ids = serializer.validated_data.get("user_ids", []) or []
        image = serializer.validated_data.get("image")
        video = serializer.validated_data.get("video")

        users, was_all_users = get_target_users_from_user_ids(user_ids)

        if user_ids and not users.exists():
            return Response(
                {"success": False, "message": "No active users found for selected user_ids."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notification = Notification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            image=image,
            video=video,
            created_by=request.user,
        )

        UserNotification.objects.bulk_create(
            [UserNotification(notification=notification, user=user) for user in users],
            ignore_conflicts=True,
        )

        for user in users:
            user_notification = UserNotification.objects.filter(notification=notification, user=user).first()
            if user_notification:
                send_realtime_notification_to_user(user, notification, user_notification)

        return Response(
            {
                "success": True,
                "message": "Notification created successfully.",
                "notification_id": notification.id,
                "sent_to": users.count(),
                "is_public": was_all_users,
                "audience_type": "All Users" if was_all_users else "Selected Users",
                "image": build_absolute_file_url(request, notification.image),
                "video": build_absolute_file_url(request, notification.video),
            },
            status=status.HTTP_201_CREATED,
        )


class MyNotificationsAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = request.user if request.user and request.user.is_authenticated else None
        total_users = get_total_active_users()

        queryset = (
            Notification.objects.all()
            .select_related("created_by")
            .annotate(recipient_count=Count("user_statuses", distinct=True))
            .order_by("-created_at")
        )

        public_query = public_notification_filter(total_users)

        if user:
            queryset = (
                queryset.filter(public_query | Q(user_statuses__user=user))
                .exclude(user_statuses__user=user, user_statuses__is_deleted=True)
                .distinct()
            )
        else:
            queryset = queryset.filter(public_query).distinct()

        # Requirement: show all available notifications, not just latest 10/50.
        notifications = list(queryset)
        status_map = get_user_status_map([item.id for item in notifications], user)

        data = [
            serialize_notification(
                request=request,
                notification=item,
                user_status=status_map.get(item.id),
                total_users=total_users,
            )
            for item in notifications
        ]

        if user:
            unread_count = UserNotification.objects.filter(
                user=user,
                is_read=False,
                is_deleted=False,
                notification_id__in=[item.id for item in notifications],
            ).count()
        else:
            unread_count = len(data)

        return Response({"success": True, "unread_count": unread_count, "notifications": data})


class MyUnreadCountAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = request.user if request.user and request.user.is_authenticated else None
        total_users = get_total_active_users()

        if user:
            unread_count = get_user_unread_count(user)
        else:
            unread_count = (
                Notification.objects.all()
                .annotate(recipient_count=Count("user_statuses", distinct=True))
                .filter(public_notification_filter(total_users))
                .count()
            )

        return Response({"success": True, "unread_count": unread_count})


class MarkNotificationReadAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            user_notification = UserNotification.objects.get(id=pk, user=request.user, is_deleted=False)
        except UserNotification.DoesNotExist:
            # Fallback for old public notifications that do not yet have a UserNotification row.
            total_users = get_total_active_users()
            try:
                notification = (
                    Notification.objects.annotate(recipient_count=Count("user_statuses", distinct=True))
                    .get(id=pk)
                )
            except Notification.DoesNotExist:
                return Response(
                    {"success": False, "message": "Notification not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not (notification.recipient_count == 0 or (total_users > 0 and notification.recipient_count >= total_users)):
                return Response(
                    {"success": False, "message": "Notification not found for this user."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            user_notification, _ = UserNotification.objects.get_or_create(
                notification=notification,
                user=request.user,
                defaults={"is_read": False, "is_deleted": False},
            )

            if user_notification.is_deleted:
                return Response(
                    {"success": False, "message": "Notification is deleted for this user."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        if not user_notification.is_read:
            user_notification.is_read = True
            user_notification.read_at = timezone.now()
            user_notification.save(update_fields=["is_read", "read_at"])

        unread_count = get_user_unread_count(request.user)

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{request.user.id}",
                {
                    "type": "send_notification",
                    "data": {
                        "action": "read_status_updated",
                        "notification_status_id": user_notification.id,
                        "notification_id": user_notification.notification_id,
                        "unread_count": unread_count,
                    },
                },
            )

        return Response({"success": True, "message": "Notification marked as read.", "unread_count": unread_count})


class MarkAllNotificationsReadAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        UserNotification.objects.filter(user=request.user, is_read=False, is_deleted=False).update(
            is_read=True,
            read_at=timezone.now(),
        )

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{request.user.id}",
                {"type": "send_notification", "data": {"action": "all_read", "unread_count": 0}},
            )

        return Response({"success": True, "message": "All notifications marked as read.", "unread_count": 0})


class DeleteNotificationAPIView(APIView):
    """
    Hide/delete a notification only for the logged-in user.
    The original admin notification stays available for other assigned users.
    """

    authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def _delete_for_user(self, request, pk):
        user_notification = UserNotification.objects.filter(id=pk, user=request.user).first()

        if not user_notification:
            # Fallback: accept notification_id for older/public rows.
            total_users = get_total_active_users()
            try:
                notification = (
                    Notification.objects.annotate(recipient_count=Count("user_statuses", distinct=True))
                    .get(id=pk)
                )
            except Notification.DoesNotExist:
                return Response(
                    {"success": False, "message": "Notification not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            existing_for_user = UserNotification.objects.filter(notification=notification, user=request.user).first()
            if existing_for_user:
                user_notification = existing_for_user
            elif notification.recipient_count == 0 or (total_users > 0 and notification.recipient_count >= total_users):
                user_notification, _ = UserNotification.objects.get_or_create(
                    notification=notification,
                    user=request.user,
                    defaults={"is_read": False, "is_deleted": False},
                )
            else:
                return Response(
                    {"success": False, "message": "Notification not found for this user."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        now = timezone.now()
        update_fields = []

        if not user_notification.is_deleted:
            user_notification.is_deleted = True
            user_notification.deleted_at = now
            update_fields.extend(["is_deleted", "deleted_at"])

        if not user_notification.is_read:
            user_notification.is_read = True
            user_notification.read_at = now
            update_fields.extend(["is_read", "read_at"])

        if update_fields:
            user_notification.save(update_fields=update_fields)

        unread_count = get_user_unread_count(request.user)

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{request.user.id}",
                {
                    "type": "send_notification",
                    "data": {
                        "action": "notification_deleted",
                        "notification_status_id": user_notification.id,
                        "notification_id": user_notification.notification_id,
                        "unread_count": unread_count,
                    },
                },
            )

        return Response(
            {
                "success": True,
                "message": "Notification deleted for this user.",
                "notification_id": user_notification.notification_id,
                "notification_status_id": user_notification.id,
                "unread_count": unread_count,
            }
        )

    def post(self, request, pk):
        return self._delete_for_user(request, pk)

    def delete(self, request, pk):
        return self._delete_for_user(request, pk)


class AdminNotificationListAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
    permission_classes = [IsAdminUserOnly]

    def get(self, request):
        notifications = Notification.objects.all().prefetch_related("user_statuses")
        serializer = AdminNotificationListSerializer(notifications, many=True, context={"request": request})
        return Response({"success": True, "notifications": serializer.data})


class AdminNotificationStatusAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
    permission_classes = [IsAdminUserOnly]

    def get(self, request, pk):
        try:
            notification = Notification.objects.get(id=pk)
        except Notification.DoesNotExist:
            return Response({"success": False, "message": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)

        statuses = UserNotification.objects.filter(notification=notification).select_related(
            "user", "user__profile", "user__login_profile"
        )
        serializer = AdminNotificationStatusSerializer(statuses, many=True)

        total_users = get_total_active_users()
        assigned_count = statuses.count()
        is_public = total_users > 0 and assigned_count >= total_users

        return Response(
            {
                "success": True,
                "notification": {
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "image": build_absolute_file_url(request, notification.image),
                    "video": build_absolute_file_url(request, notification.video),
                    "created_at": notification.created_at,
                    "total_users": assigned_count,
                    "read_count": statuses.filter(is_read=True, is_deleted=False).count(),
                    "unread_count": statuses.filter(is_read=False, is_deleted=False).count(),
                    "deleted_count": statuses.filter(is_deleted=True).count(),
                    "is_public": is_public,
                    "audience_type": "All Users" if is_public else "Selected Users",
                },
                "users": serializer.data,
            }
        )
