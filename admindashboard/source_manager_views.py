from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from users.models import UserLoginProfile
from .models import Property, AgentProfile
from .permissions import IsSourceManager
from .source_manager_serializers import SourceManagerPropertyCreateSerializer


class SourceManagerDashboardView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSourceManager]

    def get(self, request):
        profile = UserLoginProfile.objects.filter(user=request.user).first()

        total_properties = Property.objects.filter(
            contact_seller__user=request.user
        ).count()

        pending_properties = Property.objects.filter(
            contact_seller__user=request.user,
            post_status="pending"
        ).count()

        approved_properties = Property.objects.filter(
            contact_seller__user=request.user,
            post_status="publish",
            is_approved=True
        ).count()

        return Response(
            {
                "success": True,
                "user": {
                    "username": request.user.username,
                    "phone": profile.phone if profile else "",
                    "role": profile.role if profile else "",
                },
                "stats": {
                    "total_properties": total_properties,
                    "pending_properties": pending_properties,
                    "approved_properties": approved_properties,
                },
            },
            status=status.HTTP_200_OK,
        )


class SourceManagerPropertyCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSourceManager]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        agent_profile = AgentProfile.objects.filter(user=request.user).first()

        if not agent_profile:
            agent_profile = AgentProfile.objects.create(
                user=request.user,
                full_name=request.user.get_full_name() or request.user.username,
                email=request.user.email or "",
                phone="",
            )

        serializer = SourceManagerPropertyCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "agent_profile": agent_profile,
            },
        )
        serializer.is_valid(raise_exception=True)
        property_obj = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Property submitted successfully and is pending admin approval.",
                "property": {
                    "id": property_obj.id,
                    "title": property_obj.title,
                    "post_status": property_obj.post_status,
                    "is_approved": property_obj.is_approved,
                },
            },
            status=status.HTTP_201_CREATED,
        )
    



from .source_manager_list_serializers import SourceManagerMyPropertySerializer


class SourceManagerMyPropertiesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSourceManager]

    def get(self, request):
        properties = Property.objects.filter(
            contact_seller__user=request.user
        ).order_by("-created_at")

        serializer = SourceManagerMyPropertySerializer(
            properties,
            many=True,
            context={"request": request},
        )

        return Response(
            {
                "success": True,
                "count": properties.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )