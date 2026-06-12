from django.contrib import admin
from django.utils.html import format_html

from .models import JobApplication, JobOpening


@admin.register(JobOpening)
class JobOpeningAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "department",
        "location",
        "job_type",
        "work_mode",
        "is_active",
        "application_deadline",
        "display_order",
        "created_at",
    )
    list_filter = ("is_active", "job_type", "work_mode", "department", "created_at")
    search_fields = (
        "title",
        "department",
        "location",
        "description",
        "preferred_skills",
        "benefits",
        "keywords",
    )
    list_editable = ("is_active", "display_order")
    ordering = ("display_order", "-created_at")
    actions = ("activate_openings", "deactivate_openings")

    fieldsets = (
        (
            "Opening Details",
            {
                "fields": (
                    "title",
                    "department",
                    "location",
                    "job_type",
                    "work_mode",
                    "experience",
                    "salary_range",
                )
            },
        ),
        (
            "Job Content",
            {
                "fields": (
                    "description",
                    "responsibilities",
                    "requirements",
                    "preferred_skills",
                    "benefits",
                    "keywords",
                ),
                "description": "Add each point on a new line. Keywords can be comma separated.",
            },
        ),
        (
            "Visibility",
            {
                "fields": (
                    "is_active",
                    "application_deadline",
                    "display_order",
                )
            },
        ),
    )

    @admin.action(description="Activate selected openings")
    def activate_openings(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected openings")
    def deactivate_openings(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "job",
        "email",
        "phone",
        "status",
        "resume_link",
        "created_at",
    )
    list_filter = ("status", "job", "created_at")
    search_fields = ("full_name", "email", "phone", "job__title")
    readonly_fields = ("created_at", "updated_at", "resume_link")
    list_editable = ("status",)
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Application",
            {
                "fields": (
                    "job",
                    "status",
                    "full_name",
                    "email",
                    "phone",
                    "experience_years",
                    "current_company",
                    "current_ctc",
                    "expected_ctc",
                    "notice_period",
                    "cover_letter",
                    "resume",
                    "resume_link",
                    "source",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    def resume_link(self, obj):
        if obj.resume:
            return format_html('<a href="{}" target="_blank">View Resume</a>', obj.resume.url)
        return "-"

    resume_link.short_description = "Resume"
