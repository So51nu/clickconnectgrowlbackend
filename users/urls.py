# from django.urls import path
# from .views import *

# urlpatterns = [
#     path("send-otp/", SendOTPView.as_view(), name="send-otp"),
#     path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
#     path("admin-login/", admin_login, name="admin-login"),
# ]

from django.urls import path
from .views import *

urlpatterns = [
    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("admin-login/", admin_login, name="admin-login"),

    path("profile/<int:user_id>/", user_profile_detail, name="user-profile-detail"),
    path("profile/<int:user_id>/update/", user_profile_update, name="user-profile-update"),
]