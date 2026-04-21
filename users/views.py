from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import UserLoginProfile, OTPRequest
from .serializers import SendOTPSerializer, VerifyOTPSerializer
from .utils import generate_otp, normalize_phone, send_otp_sms


class SendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = normalize_phone(serializer.validated_data["phone"])
        role = serializer.validated_data["role"]

        existing_profile = UserLoginProfile.objects.filter(phone=phone).first()
        if existing_profile and existing_profile.role != role:
            return Response(
                {
                    "success": False,
                    "message": f"This mobile number is already registered as '{existing_profile.role}'. One mobile number can only be used for one role."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        recent_otp = OTPRequest.objects.filter(
            phone=phone,
            role=role,
            is_used=False,
            expires_at__gt=timezone.now()
        ).order_by("-created_at").first()

        if recent_otp:
            return Response(
                {
                    "success": False,
                    "message": "OTP already sent. Please use the current OTP or wait for expiry."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        otp = generate_otp()

        otp_request = OTPRequest.objects.create(
            phone=phone,
            role=role,
            otp=otp,
        )

        try:
            send_otp_sms(phone, otp)
        except Exception as e:
            otp_request.delete()
            return Response(
                {
                    "success": False,
                    "message": f"Failed to send OTP: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "success": True,
                "message": "OTP sent successfully."
            },
            status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = normalize_phone(serializer.validated_data["phone"])
        role = serializer.validated_data["role"]
        otp = serializer.validated_data["otp"].strip()

        otp_request = OTPRequest.objects.filter(
            phone=phone,
            role=role,
            otp=otp,
            is_used=False
        ).order_by("-created_at").first()

        if not otp_request:
            return Response(
                {
                    "success": False,
                    "message": "Invalid OTP."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_request.is_expired():
            return Response(
                {
                    "success": False,
                    "message": "OTP expired. Please request a new OTP."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = UserLoginProfile.objects.filter(phone=phone).first()

        if profile:
            if profile.role != role:
                return Response(
                    {
                        "success": False,
                        "message": f"This mobile number is already registered as '{profile.role}'. One mobile number can only be used for one role."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            user = profile.user
        else:
            base_username = f"user_{phone.replace('+', '').replace('-', '')}"
            username = base_username
            counter = 1

            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                password=None,
                first_name="",
                last_name="",
                email="",
            )

            profile = UserLoginProfile.objects.create(
                user=user,
                phone=phone,
                role=role,
                is_phone_verified=True,
            )

        profile.is_phone_verified = True
        profile.save()

        otp_request.is_used = True
        otp_request.save()

        token, _ = Token.objects.get_or_create(user=user)

        redirect_url = "/dashboard"
        if profile.role == "source_manager":
            redirect_url = "/dashboard/source-manager"

        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "phone": profile.phone,
                    "role": profile.role,
                    "is_phone_verified": profile.is_phone_verified,
                },
                "redirect_url": redirect_url,
            },
            status=status.HTTP_200_OK
        )
    


from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["POST"])
def admin_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {
                "success": False,
                "message": "Username and password are required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user is not None and (user.is_staff or user.is_superuser):
        return Response(
            {
                "success": True,
                "message": "Admin login successful.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": "admin",
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                },
                "token": f"admin-{user.id}"
            },
            status=status.HTTP_200_OK
        )

    return Response(
        {
            "success": False,
            "message": "Invalid admin credentials."
        },
        status=status.HTTP_401_UNAUTHORIZED
    )