from django.contrib import admin
from .models import ContactInquiry


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "interest", "created_at")
    search_fields = ("name", "email", "phone")
    list_filter = ("interest", "created_at")