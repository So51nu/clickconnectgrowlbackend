from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .models import CMSPage


class CMSPageAdminForm(forms.ModelForm):
    class Meta:
        model = CMSPage
        fields = "__all__"
        widgets = {
            "html_content": forms.Textarea(
                attrs={
                    "rows": 24,
                    "style": "font-family: Consolas, Monaco, monospace; font-size: 13px;",
                    "placeholder": (
                        "Paste normal HTML with inline CSS only. Example:\n"
                        "<section style=\"padding:80px 20px;\">... </section>"
                    ),
                }
            ),
            "meta_description": forms.Textarea(attrs={"rows": 3}),
        }


@admin.register(CMSPage)
class CMSPageAdmin(admin.ModelAdmin):
    form = CMSPageAdminForm
    list_display = ["title", "slug", "status", "sort_order", "frontend_link", "updated_at"]
    list_filter = ["status", "created_at", "updated_at"]
    search_fields = ["title", "slug", "html_content", "meta_title", "meta_description"]
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ["status", "sort_order"]
    readonly_fields = ["created_at", "updated_at", "frontend_preview"]
    fieldsets = (
        ("Page Details", {"fields": ("title", "slug", "status", "sort_order", "frontend_preview")} ),
        ("HTML Content", {"fields": ("html_content",)}),
        ("SEO", {"fields": ("meta_title", "meta_description", "meta_keywords")} ),
        ("Dates", {"fields": ("created_at", "updated_at")} ),
    )

    def frontend_link(self, obj):
        if not obj.slug:
            return "-"
        return format_html('<code>/cms-pages/{}</code>', obj.slug)

    frontend_link.short_description = "Frontend URL"

    def frontend_preview(self, obj):
        if not obj or not obj.slug:
            return "Save this page to generate the frontend URL."
        return format_html(
            '<div style="padding:10px 12px;background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;">'
            '<strong>Frontend URL:</strong> <code>/cms-pages/{}</code><br>'
            '<small>Add this URL in Header/Footer menu link field.</small>'
            '</div>',
            obj.slug,
        )

    frontend_preview.short_description = "Frontend Preview URL"
