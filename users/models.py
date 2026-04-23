# from django.db import models
# from django.contrib.auth.models import User
# from django.utils import timezone
# from datetime import timedelta


# class UserLoginProfile(models.Model):
#     ROLE_CHOICES = (
#         ("customer", "Customer"),
#         ("source_manager", "Source Manager"),
#     )

#     user = models.OneToOneField(
#         User,
#         on_delete=models.CASCADE,
#         related_name="login_profile"
#     )
#     phone = models.CharField(max_length=20, unique=True)
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")
#     is_phone_verified = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = "User Login Profile"
#         verbose_name_plural = "User Login Profiles"

#     def __str__(self):
#         return f"{self.phone} - {self.role}"


# class OTPRequest(models.Model):
#     ROLE_CHOICES = (
#         ("customer", "Customer"),
#         ("source_manager", "Source Manager"),
#     )

#     phone = models.CharField(max_length=20)
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES)
#     otp = models.CharField(max_length=6)
#     is_used = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField(blank=True, null=True)
#     attempt_count = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ["-created_at"]
#         verbose_name = "OTP Request"
#         verbose_name_plural = "OTP Requests"

#     def save(self, *args, **kwargs):
#         if not self.expires_at:
#             self.expires_at = timezone.now() + timedelta(minutes=5)
#         super().save(*args, **kwargs)

#     def is_expired(self):
#         return timezone.now() > self.expires_at

#     def __str__(self):
#         return f"{self.phone} - {self.role} - {self.otp}"


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class UserLoginProfile(models.Model):
    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("source_manager", "Source Manager"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="login_profile"
    )
    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")
    is_phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Login Profile"
        verbose_name_plural = "User Login Profiles"

    def __str__(self):
        return f"{self.phone} - {self.role}"


class OTPRequest(models.Model):
    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("source_manager", "Source Manager"),
    )

    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    otp = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    attempt_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "OTP Request"
        verbose_name_plural = "OTP Requests"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.phone} - {self.role} - {self.otp}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    full_name = models.CharField(max_length=150, blank=True, default="")
    full_address = models.TextField(blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    pincode = models.CharField(max_length=20, blank=True, default="")
    city = models.CharField(max_length=120, blank=True, default="")
    state = models.CharField(max_length=120, blank=True, default="")
    country = models.CharField(max_length=120, blank=True, default="")

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return self.full_name or self.user.username