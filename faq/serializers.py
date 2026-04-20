from rest_framework import serializers
from .models import FAQPageSetting, FAQCategory, FAQItem, FAQInquiry


class FAQItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQItem
        fields = ["id", "question", "answer", "order"]


class FAQCategorySerializer(serializers.ModelSerializer):
    faqs = serializers.SerializerMethodField()

    class Meta:
        model = FAQCategory
        fields = ["id", "title", "slug", "order", "faqs"]

    def get_faqs(self, obj):
        active_faqs = obj.faqs.filter(is_active=True).order_by("order", "id")
        return FAQItemSerializer(active_faqs, many=True).data


class FAQPageSettingSerializer(serializers.ModelSerializer):
    seller_image = serializers.SerializerMethodField()
    ad_image = serializers.SerializerMethodField()
    ad_logo = serializers.SerializerMethodField()

    class Meta:
        model = FAQPageSetting
        fields = [
            "section_title",
            "seller_form_title",
            "seller_name",
            "seller_phone",
            "seller_email",
            "seller_image",
            "ad_image",
            "ad_logo",
            "ad_title",
            "ad_description",
            "ad_button_text",
            "ad_button_link",
        ]

    def _build_absolute_media_url(self, obj, field_name):
        request = self.context.get("request")
        file_field = getattr(obj, field_name)
        if file_field:
            if request:
                return request.build_absolute_uri(file_field.url)
            return file_field.url
        return None

    def get_seller_image(self, obj):
        return self._build_absolute_media_url(obj, "seller_image")

    def get_ad_image(self, obj):
        return self._build_absolute_media_url(obj, "ad_image")

    def get_ad_logo(self, obj):
        return self._build_absolute_media_url(obj, "ad_logo")


class FAQPageDataSerializer(serializers.Serializer):
    page_setting = FAQPageSettingSerializer()
    categories = FAQCategorySerializer(many=True)


class FAQInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQInquiry
        fields = ["id", "full_name", "message", "created_at"]
        read_only_fields = ["id", "created_at"]