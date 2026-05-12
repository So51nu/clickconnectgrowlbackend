from rest_framework.views import APIView
from rest_framework.response import Response
from .models import FooterSection
from .serializers import FooterSectionSerializer


class FooterMenuAPIView(APIView):
    def get(self, request):
        sections = (
            FooterSection.objects
            .filter(is_active=True)
            .prefetch_related("items")
            .order_by("order", "id")
        )

        serializer = FooterSectionSerializer(sections, many=True)

        tab_sections = []
        column_sections = []

        for section in serializer.data:
            if section.get("section_type") == "tab":
                tab_sections.append(section)
            else:
                column_sections.append(section)

        return Response({
            "tabs": tab_sections,
            "columns": column_sections,
        })