# from django.contrib import admin
# from .models import UserLoginProfile, OTPRequest


# @admin.register(UserLoginProfile)
# class UserLoginProfileAdmin(admin.ModelAdmin):
#     list_display = ["id", "phone", "role", "is_phone_verified", "created_at"]
#     search_fields = ["phone", "user__username"]
#     list_filter = ["role", "is_phone_verified"]


# @admin.register(OTPRequest)
# class OTPRequestAdmin(admin.ModelAdmin):
#     list_display = ["id", "phone", "role", "otp", "is_used", "created_at", "expires_at"]
#     search_fields = ["phone", "otp"]
#     list_filter = ["role", "is_used"]

from django.contrib import admin
from .models import UserLoginProfile, OTPRequest, UserProfile


@admin.register(UserLoginProfile)
class UserLoginProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "phone", "role", "is_phone_verified", "created_at"]
    search_fields = ["phone", "user__username"]
    list_filter = ["role", "is_phone_verified"]


@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "phone", "role", "otp", "is_used", "created_at", "expires_at"]
    search_fields = ["phone", "otp"]
    list_filter = ["role", "is_used"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "full_name", "phone", "city", "state", "country"]
    search_fields = ["user__username", "full_name", "phone", "city", "state", "country"]
    list_filter = ["city", "state", "country"]