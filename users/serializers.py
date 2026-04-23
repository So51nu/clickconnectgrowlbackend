# from rest_framework import serializers


# class SendOTPSerializer(serializers.Serializer):
#     phone = serializers.CharField(max_length=20)
#     role = serializers.ChoiceField(choices=["customer", "source_manager"])


# class VerifyOTPSerializer(serializers.Serializer):
#     phone = serializers.CharField(max_length=20)
#     role = serializers.ChoiceField(choices=["customer", "source_manager"])
#     otp = serializers.CharField(max_length=6)

from rest_framework import serializers


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    role = serializers.ChoiceField(choices=["customer", "source_manager"])


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    role = serializers.ChoiceField(choices=["customer", "source_manager"])
    otp = serializers.CharField(max_length=6)


class UserProfileUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    full_address = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    pincode = serializers.CharField(max_length=20, required=False, allow_blank=True)
    city = serializers.CharField(max_length=120, required=False, allow_blank=True)
    state = serializers.CharField(max_length=120, required=False, allow_blank=True)
    country = serializers.CharField(max_length=120, required=False, allow_blank=True)