import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


STATUS_CHOICES = (
    ("draft", "Draft"),
    ("published", "Published"),
)


RESERVED_SLUGS = {
    "admin",
    "api",
    "login",
    "sellogin",
    "dashboard",
    "userdashboard",
    "agents",
    "agency",
    "blogs",
    "home",
    "otherpages",
    "project",
    "projects",
    "properties",
    "property-details",
    "search",
    "contact",
    "career",
    "careers",
    "cms-pages",
}


def clean_html_content(value: str) -> str:
    """
    Basic safety cleanup for admin-created HTML pages.
    Inline CSS is allowed, but script tags, inline JS events, and javascript: URLs are removed.
    """
    if not value:
        return ""

    cleaned = value
    cleaned = re.sub(r"<\s*script\b[^>]*>.*?<\s*/\s*script\s*>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"\s+on[a-zA-Z]+\s*=\s*(['\"]).*?\1", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"\s+on[a-zA-Z]+\s*=\s*[^\s>]+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"javascript\s*:", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


class CMSPage(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="Example: hr-compliance-policy. Frontend URL: /cms-pages/hr-compliance-policy",
    )
    html_content = models.TextField(
        help_text="Paste normal HTML with inline CSS only. Do not paste React/JSX code or script tags."
    )
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CMS Page"
        verbose_name_plural = "CMS Pages"
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()

        if self.slug:
            self.slug = slugify(self.slug)

        if not self.slug:
            raise ValidationError({"slug": "Slug is required."})

        if self.slug in RESERVED_SLUGS:
            raise ValidationError(
                {
                    "slug": (
                        "This slug is reserved. Use another slug. "
                        "CMS frontend URL will be /cms-pages/<your-slug>."
                    )
                }
            )

        if self.html_content:
            self.html_content = clean_html_content(self.html_content)

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        self.full_clean()
        return super().save(*args, **kwargs)
