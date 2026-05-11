from django.db import models


class HeaderMenu(models.Model):
    MATCH_TYPE_CHOICES = [
        ("exact", "Exact Match"),
        ("starts_with", "Starts With"),
        ("custom_blog", "Custom Blog Match"),
    ]

    key = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text="Example: home, listing, cities, developers, faq, blog, contact, about",
    )

    title = models.CharField(max_length=100)
    path = models.CharField(
        max_length=255,
        help_text="Example: /, /cities, /contact",
    )
    match_type = models.CharField(
        max_length=30,
        choices=MATCH_TYPE_CHOICES,
        default="exact",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Header Menu"
        verbose_name_plural = "Header Menus"

    def __str__(self):
        return f"{self.title} ({self.key})"