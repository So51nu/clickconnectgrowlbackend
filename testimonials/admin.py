from django.contrib import admin
from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "role",
        "rating",
        "is_active",
        "sort_order",
        "created_at",
    )
    list_filter = ("is_active", "rating")
    search_fields = ("name", "role", "description")
    ordering = ("sort_order", "-id")