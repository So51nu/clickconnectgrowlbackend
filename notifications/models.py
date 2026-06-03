from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = (
        ("general", "General"),
        ("property", "Property"),
        ("lead", "Lead"),
        ("system", "System"),
        ("offer", "Offer"),
    )

    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        default="general"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_notifications"
    )

    recipients = models.ManyToManyField(
        User,
        through="UserNotification",
        related_name="received_notifications"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return self.title


class UserNotification(models.Model):
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="user_statuses"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_statuses"
    )

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    delivered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("notification", "user")
        ordering = ["-delivered_at"]
        verbose_name = "User Notification"
        verbose_name_plural = "User Notifications"

    def __str__(self):
        return f"{self.user.username} - {self.notification.title}"