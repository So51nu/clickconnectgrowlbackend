from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from .models import FAQPageSetting, FAQCategory, FAQInquiry
from .serializers import (
    FAQPageSettingSerializer,
    FAQCategorySerializer,
    FAQInquirySerializer,
)


class FAQPageDataView(APIView):
    def get(self, request, *args, **kwargs):
        page_setting = FAQPageSetting.objects.filter(is_active=True).first()
        categories = FAQCategory.objects.filter(is_active=True).order_by("order", "id")

        if not page_setting:
            page_setting = FAQPageSetting.objects.create(
                section_title="Frequently Asked Questions",
                seller_form_title="Contact Sellers",
                seller_name="Growl Real Estate Seller",
            )

        page_setting_data = FAQPageSettingSerializer(
            page_setting,
            context={"request": request}
        ).data
        categories_data = FAQCategorySerializer(categories, many=True).data

        return Response(
            {
                "success": True,
                "page_setting": page_setting_data,
                "categories": categories_data,
            },
            status=status.HTTP_200_OK,
        )


class FAQInquiryCreateView(CreateAPIView):
    queryset = FAQInquiry.objects.all()
    serializer_class = FAQInquirySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                "success": True,
                "message": "Your inquiry has been submitted successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )