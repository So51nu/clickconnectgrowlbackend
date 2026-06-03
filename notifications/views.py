# from django.contrib.auth.models import User
# from django.db.models import Q
# from django.utils import timezone

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from rest_framework.authentication import TokenAuthentication, SessionAuthentication

# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer
# from .authentication import BearerTokenAuthentication
# from .models import Notification, UserNotification
# from .serializers import (
#     NotificationUserSerializer,
#     UserNotificationSerializer,
#     AdminNotificationCreateSerializer,
#     AdminNotificationListSerializer,
#     AdminNotificationStatusSerializer,
# )


# class IsAdminUserOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_authenticated and request.user.is_staff)


# class AdminSearchUsersAPIView(APIView):
#     authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
#     permission_classes = [IsAdminUserOnly]

#     def get(self, request):
#         search = request.GET.get("search", "").strip()
#         role = request.GET.get("role", "").strip()

#         users = User.objects.all().order_by("-id")

#         if search:
#             users = users.filter(
#                 Q(username__icontains=search)
#                 | Q(email__icontains=search)
#                 | Q(profile__full_name__icontains=search)
#                 | Q(profile__phone__icontains=search)
#                 | Q(login_profile__phone__icontains=search)
#             )

#         if role:
#             users = users.filter(login_profile__role=role)

#         users = users.distinct()[:50]

#         serializer = NotificationUserSerializer(users, many=True)
#         return Response({
#             "success": True,
#             "users": serializer.data
#         })


# class AdminCreateNotificationAPIView(APIView):
#     authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
#     permission_classes = [IsAdminUserOnly]

#     def post(self, request):
#         serializer = AdminNotificationCreateSerializer(data=request.data)

#         if not serializer.is_valid():
#             return Response({
#                 "success": False,
#                 "errors": serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)

#         title = serializer.validated_data["title"]
#         message = serializer.validated_data["message"]
#         notification_type = serializer.validated_data["notification_type"]
#         user_ids = serializer.validated_data["user_ids"]
#         user_notification = UserNotification.objects.get(
#             notification=notification,
#             user=user
#         )
#         users = User.objects.filter(id__in=user_ids, is_active=True)

#         if not users.exists():
#             return Response({
#                 "success": False,
#                 "message": "No active users found."
#             }, status=status.HTTP_400_BAD_REQUEST)

#         notification = Notification.objects.create(
#             title=title,
#             message=message,
#             notification_type=notification_type,
#             created_by=request.user
#         )

#         user_notification_objects = [
#             UserNotification(notification=notification, user=user)
#             for user in users
#         ]

#         UserNotification.objects.bulk_create(user_notification_objects, ignore_conflicts=True)

#         channel_layer = get_channel_layer()

#         for user in users:
#             unread_count = UserNotification.objects.filter(
#                 user=user,
#                 is_read=False
#             ).count()

#             payload = {
#                 "type": "send_notification",
#                 "data": {
#                     "notification_id": notification.id,
#                     "title": notification.title,
#                     "message": notification.message,
#                     "notification_type": notification.notification_type,
#                     "created_at": notification.created_at.isoformat(),
#                     "unread_count": unread_count,
#                     "user_notification_id": user_notification.id,
#                 }
#             }

#             async_to_sync(channel_layer.group_send)(
#                 f"user_{user.id}",
#                 payload
#             )

#         return Response({
#             "success": True,
#             "message": "Notification sent successfully.",
#             "notification_id": notification.id,
#             "sent_to": users.count()
#         }, status=status.HTTP_201_CREATED)


# class MyNotificationsAPIView(APIView):
#     authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         notifications = UserNotification.objects.filter(
#             user=request.user
#         ).select_related("notification", "notification__created_by")

#         serializer = UserNotificationSerializer(notifications, many=True)

#         unread_count = notifications.filter(is_read=False).count()

#         return Response({
#             "success": True,
#             "unread_count": unread_count,
#             "notifications": serializer.data
#         })


# class MyUnreadCountAPIView(APIView):
#     authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         unread_count = UserNotification.objects.filter(
#             user=request.user,
#             is_read=False
#         ).count()

#         return Response({
#             "success": True,
#             "unread_count": unread_count
#         })


# class MarkNotificationReadAPIView(APIView):
#     authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, pk):
#         try:
#             user_notification = UserNotification.objects.get(
#                 id=pk,
#                 user=request.user
#             )
#         except UserNotification.DoesNotExist:
#             return Response({
#                 "success": False,
#                 "message": "Notification not found."
#             }, status=status.HTTP_404_NOT_FOUND)

#         if not user_notification.is_read:
#             user_notification.is_read = True
#             user_notification.read_at = timezone.now()
#             user_notification.save(update_fields=["is_read", "read_at"])

#         unread_count = UserNotification.objects.filter(
#             user=request.user,
#             is_read=False
#         ).count()

#         channel_layer = get_channel_layer()

#         async_to_sync(channel_layer.group_send)(
#             f"user_{request.user.id}",
#             {
#                 "type": "send_notification",
#                 "data": {
#                     "action": "read_status_updated",
#                     "notification_status_id": user_notification.id,
#                     "unread_count": unread_count,
#                 }
#             }
#         )

#         return Response({
#             "success": True,
#             "message": "Notification marked as read.",
#             "unread_count": unread_count
#         })


# class MarkAllNotificationsReadAPIView(APIView):
#     authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         UserNotification.objects.filter(
#             user=request.user,
#             is_read=False
#         ).update(
#             is_read=True,
#             read_at=timezone.now()
#         )

#         channel_layer = get_channel_layer()

#         async_to_sync(channel_layer.group_send)(
#             f"user_{request.user.id}",
#             {
#                 "type": "send_notification",
#                 "data": {
#                     "action": "all_read",
#                     "unread_count": 0,
#                 }
#             }
#         )

#         return Response({
#             "success": True,
#             "message": "All notifications marked as read.",
#             "unread_count": 0
#         })


# class AdminNotificationListAPIView(APIView):
#     authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
#     permission_classes = [IsAdminUserOnly]

#     def get(self, request):
#         notifications = Notification.objects.all().prefetch_related("user_statuses")
#         serializer = AdminNotificationListSerializer(notifications, many=True)

#         return Response({
#             "success": True,
#             "notifications": serializer.data
#         })


# class AdminNotificationStatusAPIView(APIView):
#     authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
#     permission_classes = [IsAdminUserOnly]

#     def get(self, request, pk):
#         try:
#             notification = Notification.objects.get(id=pk)
#         except Notification.DoesNotExist:
#             return Response({
#                 "success": False,
#                 "message": "Notification not found."
#             }, status=status.HTTP_404_NOT_FOUND)

#         statuses = UserNotification.objects.filter(
#             notification=notification
#         ).select_related("user", "user__profile", "user__login_profile")

#         serializer = AdminNotificationStatusSerializer(statuses, many=True)

#         return Response({
#             "success": True,
#             "notification": {
#                 "id": notification.id,
#                 "title": notification.title,
#                 "message": notification.message,
#                 "notification_type": notification.notification_type,
#                 "created_at": notification.created_at,
#                 "total_users": statuses.count(),
#                 "read_count": statuses.filter(is_read=True).count(),
#                 "unread_count": statuses.filter(is_read=False).count(),
#             },
#             "users": serializer.data
#         })




from django.contrib.auth.models import User
from django.db.models import Q, Count, Prefetch
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import SessionAuthentication

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .authentication import BearerTokenAuthentication
from .models import Notification, UserNotification
from .serializers import (
    NotificationUserSerializer,
    UserNotificationSerializer,
    AdminNotificationCreateSerializer,
    AdminNotificationListSerializer,
    AdminNotificationStatusSerializer,
)


class IsAdminUserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


def get_total_active_users():
    return User.objects.filter(is_active=True).count()


def public_notification_filter(total_users):
    # Public/general notification rules:
    # 1) No recipient selected = public/general, show without login.
    # 2) Assigned to all active users = show without login also.
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


def serialize_notification(notification, user_status=None, total_users=0):
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
        # id should stay UserNotification id for assigned notifications, because existing mark-read API uses status id.
        # For public notifications, there is no UserNotification row, so use notification id and keep user_notification_id null.
        "id": user_status.id if user_status else notification.id,
        "notification_id": notification.id,
        "user_notification_id": user_status.id if user_status else None,
        "title": notification.title,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "is_read": bool(user_status.is_read) if user_status else False,
        "read_at": user_status.read_at if user_status else None,
        "delivered_at": user_status.delivered_at if user_status else notification.created_at,
        "created_at": notification.created_at,
        "created_by": created_by,
        "is_public": is_public,
        "recipient_count": recipient_count,
    }


def send_realtime_notification_to_user(user, notification, user_notification):
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

    def post(self, request):
        serializer = AdminNotificationCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        title = serializer.validated_data["title"]
        message = serializer.validated_data["message"]
        notification_type = serializer.validated_data["notification_type"]
        user_ids = serializer.validated_data.get("user_ids", []) or []

        notification = Notification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            created_by=request.user,
        )

        users = User.objects.filter(id__in=user_ids, is_active=True).distinct()

        user_notification_objects = [
            UserNotification(notification=notification, user=user)
            for user in users
        ]

        created_statuses = UserNotification.objects.bulk_create(
            user_notification_objects,
            ignore_conflicts=True,
        )

        # Realtime only for logged-in assigned users. Public/unassigned notifications will show through polling/API.
        for user in users:
            user_notification = UserNotification.objects.filter(
                notification=notification,
                user=user,
            ).first()
            send_realtime_notification_to_user(user, notification, user_notification)

        return Response({
            "success": True,
            "message": "Notification created successfully.",
            "notification_id": notification.id,
            "sent_to": users.count(),
            "is_public": users.count() == 0,
        }, status=status.HTTP_201_CREATED)


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
            queryset = queryset.filter(public_query | Q(user_statuses__user=user)).distinct()
        else:
            queryset = queryset.filter(public_query).distinct()

        notifications = list(queryset[:50])
        status_map = get_user_status_map([item.id for item in notifications], user)

        data = [
            serialize_notification(
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
                notification_id__in=[item.id for item in notifications],
            ).count()
        else:
            # Public users do not have read state, so show count as public notification count.
            unread_count = len(data)

        return Response({
            "success": True,
            "unread_count": unread_count,
            "notifications": data,
        })


class MyUnreadCountAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = request.user if request.user and request.user.is_authenticated else None
        total_users = get_total_active_users()

        if user:
            unread_count = UserNotification.objects.filter(user=user, is_read=False).count()
        else:
            queryset = (
                Notification.objects.all()
                .annotate(recipient_count=Count("user_statuses", distinct=True))
                .filter(public_notification_filter(total_users))
            )
            unread_count = queryset.count()

        return Response({"success": True, "unread_count": unread_count})


class MarkNotificationReadAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            user_notification = UserNotification.objects.get(id=pk, user=request.user)
        except UserNotification.DoesNotExist:
            return Response({
                "success": True,
                "message": "Public notification does not require user-specific read status.",
                "unread_count": UserNotification.objects.filter(user=request.user, is_read=False).count(),
            }, status=status.HTTP_200_OK)

        if not user_notification.is_read:
            user_notification.is_read = True
            user_notification.read_at = timezone.now()
            user_notification.save(update_fields=["is_read", "read_at"])

        unread_count = UserNotification.objects.filter(user=request.user, is_read=False).count()

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{request.user.id}",
                {
                    "type": "send_notification",
                    "data": {
                        "action": "read_status_updated",
                        "notification_status_id": user_notification.id,
                        "unread_count": unread_count,
                    },
                },
            )

        return Response({
            "success": True,
            "message": "Notification marked as read.",
            "unread_count": unread_count,
        })


class MarkAllNotificationsReadAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        UserNotification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(
            is_read=True,
            read_at=timezone.now(),
        )

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{request.user.id}",
                {
                    "type": "send_notification",
                    "data": {
                        "action": "all_read",
                        "unread_count": 0,
                    },
                },
            )

        return Response({
            "success": True,
            "message": "All assigned notifications marked as read.",
            "unread_count": 0,
        })


class AdminNotificationListAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
    permission_classes = [IsAdminUserOnly]

    def get(self, request):
        notifications = Notification.objects.all().prefetch_related("user_statuses")
        serializer = AdminNotificationListSerializer(notifications, many=True)

        return Response({
            "success": True,
            "notifications": serializer.data,
        })


class AdminNotificationStatusAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, SessionAuthentication]
    permission_classes = [IsAdminUserOnly]

    def get(self, request, pk):
        try:
            notification = Notification.objects.get(id=pk)
        except Notification.DoesNotExist:
            return Response({
                "success": False,
                "message": "Notification not found.",
            }, status=status.HTTP_404_NOT_FOUND)

        statuses = UserNotification.objects.filter(
            notification=notification,
        ).select_related("user", "user__profile", "user__login_profile")

        serializer = AdminNotificationStatusSerializer(statuses, many=True)

        total_users = get_total_active_users()
        assigned_count = statuses.count()
        is_public = assigned_count == 0 or (total_users > 0 and assigned_count >= total_users)

        return Response({
            "success": True,
            "notification": {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "created_at": notification.created_at,
                "total_users": assigned_count,
                "read_count": statuses.filter(is_read=True).count(),
                "unread_count": statuses.filter(is_read=False).count(),
                "is_public": is_public,
            },
            "users": serializer.data,
        })
