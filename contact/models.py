from django.db import models


class ContactInquiry(models.Model):
    INTEREST_CHOICES = (
        ("buy", "Buy"),
        ("sell", "Sell"),
    )

    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    interest = models.CharField(max_length=20, choices=INTEREST_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"

    def __str__(self):
        return f"{self.name} - {self.phone}"
