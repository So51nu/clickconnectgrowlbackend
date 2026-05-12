from django.contrib import admin
from .models import FooterSection, FooterMenuItem


class FooterMenuItemInline(admin.TabularInline):
    model = FooterMenuItem
    extra = 0
    fields = ("title", "url", "order", "is_active", "is_login_modal")
    ordering = ("order", "id")


@admin.action(description="Mark selected sections as Active")
def make_sections_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Mark selected sections as Inactive")
def make_sections_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.action(description="Mark selected menu items as Active")
def make_items_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Mark selected menu items as Inactive")
def make_items_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.register(FooterSection)
class FooterSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "section_type", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("section_type", "is_active")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "id")
    inlines = [FooterMenuItemInline]
    actions = [make_sections_active, make_sections_inactive]


@admin.register(FooterMenuItem)
class FooterMenuItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "section",
        "url",
        "order",
        "is_active",
        "is_login_modal",
    )
    list_editable = ("order", "is_active", "is_login_modal")
    list_filter = ("section", "is_active", "is_login_modal")
    search_fields = ("title", "url", "section__title")
    ordering = ("section__order", "order", "id")
    actions = [make_items_active, make_items_inactive]