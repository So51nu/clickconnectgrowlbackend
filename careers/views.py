from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import JobOpening
from .serializers import JobApplicationSerializer, JobOpeningSerializer


class JobOpeningListView(APIView):
    def get(self, request, *args, **kwargs):
        openings = JobOpening.objects.filter(is_active=True)

        valid_openings = [
            opening for opening in openings if not opening.is_deadline_over
        ]

        serializer = JobOpeningSerializer(valid_openings, many=True)

        return Response(
            {
                "success": True,
                "count": len(serializer.data),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class JobApplicationCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = JobApplicationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        application = serializer.save(source="Website")
        submitted_at_ist = timezone.localtime(application.created_at).strftime(
            "%d %b %Y, %I:%M %p"
        )

        recipient_email = getattr(
            settings,
            "HR_NOTIFICATION_EMAIL",
            getattr(
                settings,
                "CONTACT_NOTIFICATION_EMAIL",
                "realestate@growlcommunications.com",
            ),
        )

        subject = f"New Career Application - {application.job.title}"
        email_body = f"""
New job application received from Growl City Realty website.

Job Opening: {application.job.title}
Department: {application.job.department or 'Not provided'}
Location: {application.job.location or 'Not provided'}
Job Type: {application.job.get_job_type_display()}
Work Mode: {application.job.get_work_mode_display()}

Candidate Name: {application.full_name}
Email: {application.email}
Phone: {application.phone}
Experience: {application.experience_years or 'Not provided'}
Current Company: {application.current_company or 'Not provided'}
Current CTC: {application.current_ctc or 'Not provided'}
Expected CTC: {application.expected_ctc or 'Not provided'}
Notice Period: {application.notice_period or 'Not provided'}

Cover Letter:
{application.cover_letter or 'Not provided'}

Submitted At: {submitted_at_ist} IST
""".strip()

        email_sent = False
        email_error = ""

        try:
            email = EmailMessage(
                subject=subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
                reply_to=[application.email],
            )

            if application.resume:
                email.attach_file(application.resume.path)

            email.send(fail_silently=False)
            email_sent = True
        except Exception as error:
            email_error = str(error)

        return Response(
            {
                "success": True,
                "message": "Application submitted successfully.",
                "notification_email": recipient_email,
                "email_sent": email_sent,
                "email_error": email_error,
                "data": JobApplicationSerializer(application).data,
            },
            status=status.HTTP_201_CREATED,
        )
