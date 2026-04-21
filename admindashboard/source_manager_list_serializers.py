from rest_framework import serializers
from .models import Property


class SourceManagerMyPropertySerializer(serializers.ModelSerializer):
    contact_seller_name = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "price",
            "full_address",
            "city",
            "developer_name",
            "property_code",
            "property_type",
            "property_status",
            "post_status",
            "is_approved",
            "created_at",
            "contact_seller_name",
            "primary_image",
        ]

    def get_contact_seller_name(self, obj):
        if obj.contact_seller:
            return obj.contact_seller.full_name
        return ""

    def get_primary_image(self, obj):
        request = self.context.get("request")
        primary = obj.images.filter(is_primary=True).first() or obj.images.first()

        if primary and primary.image:
            if request:
                return request.build_absolute_uri(primary.image.url)
            return primary.image.url
        return None