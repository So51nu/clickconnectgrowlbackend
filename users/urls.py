from django.urls import path
from .views import *

urlpatterns = [
    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("admin-login/", admin_login, name="admin-login"),
]