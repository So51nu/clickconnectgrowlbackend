# from django.urls import path
# from .views import (
#     AdminSearchUsersAPIView,
#     AdminCreateNotificationAPIView,
#     MyNotificationsAPIView,
#     MyUnreadCountAPIView,
#     MarkNotificationReadAPIView,
#     MarkAllNotificationsReadAPIView,
#     AdminNotificationListAPIView,
#     AdminNotificationStatusAPIView,
# )

# urlpatterns = [
#     # Admin APIs
#     path("admin/search-users/", AdminSearchUsersAPIView.as_view(), name="admin-search-users"),
#     path("admin/create/", AdminCreateNotificationAPIView.as_view(), name="admin-create-notification"),
#     path("admin/list/", AdminNotificationListAPIView.as_view(), name="admin-notification-list"),
#     path("admin/<int:pk>/status/", AdminNotificationStatusAPIView.as_view(), name="admin-notification-status"),

#     # User APIs
#     path("my/", MyNotificationsAPIView.as_view(), name="my-notifications"),
#     path("unread-count/", MyUnreadCountAPIView.as_view(), name="my-unread-count"),
#     path("mark-read/<int:pk>/", MarkNotificationReadAPIView.as_view(), name="mark-notification-read"),
#     path("mark-all-read/", MarkAllNotificationsReadAPIView.as_view(), name="mark-all-notifications-read"),
# ]



from django.urls import path
from .views import (
    AdminSearchUsersAPIView,
    AdminCreateNotificationAPIView,
    MyNotificationsAPIView,
    MyUnreadCountAPIView,
    MarkNotificationReadAPIView,
    MarkAllNotificationsReadAPIView,
    AdminNotificationListAPIView,
    AdminNotificationStatusAPIView,
)

urlpatterns = [
    # Admin APIs
    path("admin/search-users/", AdminSearchUsersAPIView.as_view(), name="admin-search-users"),
    path("admin/create/", AdminCreateNotificationAPIView.as_view(), name="admin-create-notification"),
    path("admin/list/", AdminNotificationListAPIView.as_view(), name="admin-notification-list"),
    path("admin/<int:pk>/status/", AdminNotificationStatusAPIView.as_view(), name="admin-notification-status"),

    # User APIs
    path("my/", MyNotificationsAPIView.as_view(), name="my-notifications"),
    path("unread-count/", MyUnreadCountAPIView.as_view(), name="my-unread-count"),
    path("mark-read/<int:pk>/", MarkNotificationReadAPIView.as_view(), name="mark-notification-read"),
    path("mark-all-read/", MarkAllNotificationsReadAPIView.as_view(), name="mark-all-notifications-read"),
]