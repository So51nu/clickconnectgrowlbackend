from django.contrib import admin
from .models import FAQPageSetting, FAQCategory, FAQItem, FAQInquiry


class FAQItemInline(admin.TabularInline):
    model = FAQItem
    extra = 1


@admin.register(FAQPageSetting)
class FAQPageSettingAdmin(admin.ModelAdmin):
    list_display = ["section_title", "seller_name", "is_active"]


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "order", "is_active"]
    list_editable = ["order", "is_active"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [FAQItemInline]


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ["question", "category", "order", "is_active"]
    list_filter = ["category", "is_active"]
    list_editable = ["order", "is_active"]


@admin.register(FAQInquiry)
class FAQInquiryAdmin(admin.ModelAdmin):
    list_display = ["full_name", "created_at"]
    readonly_fields = ["created_at"]