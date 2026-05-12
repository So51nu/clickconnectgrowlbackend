from django.db import models
from django.utils.text import slugify


class FooterSection(models.Model):
    SECTION_TYPES = (
        ("tab", "Top Tab Section"),
        ("column", "Footer Column Section"),
    )

    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    section_type = models.CharField(
        max_length=20,
        choices=SECTION_TYPES,
        default="column"
    )
    order = models.PositiveIntegerField(default=0)

    # Active = show on frontend, Inactive = hide on frontend
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Footer Section"
        verbose_name_plural = "Footer Sections"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.title} ({status})"


class FooterMenuItem(models.Model):
    section = models.ForeignKey(
        FooterSection,
        on_delete=models.CASCADE,
        related_name="items"
    )
    title = models.CharField(max_length=160)
    url = models.CharField(max_length=255, default="/")
    order = models.PositiveIntegerField(default=0)

    # Active = show on frontend, Inactive = hide on frontend
    is_active = models.BooleanField(default=True)

    is_login_modal = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Footer Menu Item"
        verbose_name_plural = "Footer Menu Items"

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.section.title} - {self.title} ({status})"