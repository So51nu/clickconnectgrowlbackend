from rest_framework import serializers


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    role = serializers.ChoiceField(choices=["customer", "source_manager"])


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    role = serializers.ChoiceField(choices=["customer", "source_manager"])
    otp = serializers.CharField(max_length=6)