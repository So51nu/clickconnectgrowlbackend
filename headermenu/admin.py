from django.contrib import admin
from .models import HeaderMenu


@admin.register(HeaderMenu)
class HeaderMenuAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "title",
        "path",
        "match_type",
        "order",
        "is_active",
    )
    list_editable = (
        "title",
        "path",
        "match_type",
        "order",
        "is_active",
    )
    search_fields = ("key", "title", "path")
    list_filter = ("is_active", "match_type")
    ordering = ("order", "id")