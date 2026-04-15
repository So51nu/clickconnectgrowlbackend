from rest_framework import serializers
from .models import ContactInquiry


class ContactInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInquiry
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

    def validate_phone(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits.")
        return value