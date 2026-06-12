import re
from rest_framework import serializers
from .models import ContactInquiry


class ContactInquirySerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = ContactInquiry
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

    def validate_interest(self, value):
        value = str(value or "").strip().lower()
        if value not in ["buy", "sell"]:
            raise serializers.ValidationError("Interested In must be Buy or Sell.")
        return value

    def validate_phone(self, value):
        raw_value = str(value or "").strip()
        cleaned = re.sub(r"[\s\-()]", "", raw_value)

        if cleaned.startswith("+91"):
            mobile = cleaned[3:]
        elif cleaned.startswith("91") and len(cleaned) == 12:
            mobile = cleaned[2:]
        else:
            mobile = cleaned

        if not re.fullmatch(r"[6-9]\d{9}", mobile):
            raise serializers.ValidationError(
                "Phone number must be +91 followed by 10 digits and must start with 6, 7, 8, or 9."
            )

        return f"+91{mobile}"

    def validate_email(self, value):
        if value in [None, ""]:
            return ""
        return str(value).strip().lower()
