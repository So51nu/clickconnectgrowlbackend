from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ContactInquirySerializer


class ContactInquiryCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ContactInquirySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Contact inquiry submitted successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )