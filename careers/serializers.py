import os
import re

from rest_framework import serializers

from .models import JobApplication, JobOpening


class JobOpeningSerializer(serializers.ModelSerializer):
    job_type_display = serializers.CharField(source="get_job_type_display", read_only=True)
    work_mode_display = serializers.CharField(source="get_work_mode_display", read_only=True)

    class Meta:
        model = JobOpening
        fields = [
            "id",
            "title",
            "department",
            "location",
            "job_type",
            "job_type_display",
            "work_mode",
            "work_mode_display",
            "experience",
            "salary_range",
            "description",
            "responsibilities",
            "requirements",
            "preferred_skills",
            "benefits",
            "keywords",
            "application_deadline",
            "display_order",
            "created_at",
        ]


class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "job",
            "job_title",
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
            "status",
            "source",
            "created_at",
        ]
        read_only_fields = ["id", "job_title", "status", "source", "created_at"]

    def validate_job(self, value):
        if not value.is_active:
            raise serializers.ValidationError("This opening is currently closed.")

        if value.is_deadline_over:
            raise serializers.ValidationError("Application deadline is over for this opening.")

        return value

    def validate_phone(self, value):
        digits = re.sub(r"\D", "", str(value or ""))

        if digits.startswith("91") and len(digits) == 12:
            digits = digits[2:]

        if not re.match(r"^[6-9]\d{9}$", digits):
            raise serializers.ValidationError(
                "Enter a valid 10 digit mobile number starting with 6, 7, 8 or 9."
            )

        return f"+91{digits}"

    def validate_resume(self, value):
        allowed_extensions = [".pdf", ".doc", ".docx"]
        extension = os.path.splitext(value.name)[1].lower()

        if extension not in allowed_extensions:
            raise serializers.ValidationError("Resume must be a PDF, DOC or DOCX file.")

        max_size = 5 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("Resume file size must be less than 5 MB.")

        return value
