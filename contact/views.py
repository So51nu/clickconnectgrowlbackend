from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ContactInquirySerializer


class ContactInquiryCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ContactInquirySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        inquiry = serializer.save()
        email_missing = not bool(inquiry.email)

        # Convert created_at UTC time to project timezone from settings.py.
        # Make sure settings.py has:
        # TIME_ZONE = "Asia/Kolkata"
        # USE_TZ = True
        submitted_at_ist = timezone.localtime(inquiry.created_at).strftime(
            "%d %b %Y, %I:%M %p"
        )

        subject = "New Contact Inquiry - Growl City Realty"
        email_body = f"""
New contact inquiry received from Growl City Realty website.

Name: {inquiry.name}
Email: {inquiry.email or 'Not provided'}
Phone: {inquiry.phone}
Interested In: {inquiry.get_interest_display()}
Message: {inquiry.message}
Submitted At: {submitted_at_ist} IST
""".strip()

        recipient_email = getattr(
            settings,
            "CONTACT_NOTIFICATION_EMAIL",
            "realestate@growlcommunications.com",
        )

        email_sent = False
        email_error = ""

        try:
            email = EmailMessage(
                subject=subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
                reply_to=[inquiry.email] if inquiry.email else None,
            )
            email.send(fail_silently=False)
            email_sent = True
        except Exception as error:
            email_error = str(error)

        response_message = "Contact inquiry submitted successfully."
        if email_missing:
            response_message += " You forgot to add the email address."

        return Response(
            {
                "success": True,
                "message": response_message,
                "email_missing": email_missing,
                "notification_email": recipient_email,
                "email_sent": email_sent,
                "email_error": email_error,
                "data": ContactInquirySerializer(inquiry).data,
            },
            status=status.HTTP_201_CREATED,
        )
