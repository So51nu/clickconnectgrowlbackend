
from rest_framework import serializers
from .models import (
    AgentProfile,
    PackagePlan,
    Property,
    PropertyImage,
    PropertyFloorPlan,
    Review,
    SaveSearch,
)


class PropertyImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = ["id", "image", "image_url", "is_primary"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        if obj.image:
            return obj.image.url
        return ""


class PropertyFloorPlanSerializer(serializers.ModelSerializer):
    floor_image_url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyFloorPlan
        fields = [
            "id",
            "floor_name",
            "floor_price",
            "price_postfix",
            "floor_size",
            "size_postfix",
            "bedrooms",
            "bathrooms",
            "description",
            "floor_image",
            "floor_image_url",
        ]

    def get_floor_image_url(self, obj):
        request = self.context.get("request")
        if obj.floor_image and request:
            return request.build_absolute_uri(obj.floor_image.url)
        if obj.floor_image:
            return obj.floor_image.url
        return ""


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    floor_plans = PropertyFloorPlanSerializer(many=True, read_only=True)
    imageSrc = serializers.SerializerMethodField()
    postingDate = serializers.SerializerMethodField()
    expiryDate = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "description",
            "full_address",
            "zip_code",
            "country",
            "state",
            "neighborhood",
            "location",
            "map_embed_url",
            "price",
            "unit_price",
            "before_price_label",
            "after_price_label",
            "property_type",
            "property_status",
            "property_label",
            "post_status",
            "size_sqft",
            "land_area_sqft",
            "property_code",
            "rooms",
            "bedrooms",
            "bathrooms",
            "garages",
            "garages_size_sqft",
            "year_built",
            "amenities",
            "virtual_tour_type",
            "virtual_tour_embed_code",
            "video_url",
            "is_favorite",
            "is_approved",
            "posting_date",
            "expiry_date",
            "postingDate",
            "expiryDate",
            "imageSrc",
            "images",
            "floor_plans",
        ]

    def get_imageSrc(self, obj):
        request = self.context.get("request")
        primary = obj.images.filter(is_primary=True).first() or obj.images.first()
        if primary and primary.image:
            if request:
                return request.build_absolute_uri(primary.image.url)
            return primary.image.url
        return ""

    def get_postingDate(self, obj):
        return obj.posting_date.strftime("%b %d, %Y") if obj.posting_date else ""

    def get_expiryDate(self, obj):
        return obj.expiry_date.strftime("%b %d, %Y") if obj.expiry_date else "No Expiry"


class AgentProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    poster_url = serializers.SerializerMethodField()

    class Meta:
        model = AgentProfile
        fields = [
            "id",
            "full_name",
            "description",
            "company",
            "position",
            "office_number",
            "office_address",
            "job",
            "email",
            "phone",
            "location",
            "facebook",
            "twitter",
            "linkedin",
            "avatar",
            "poster",
            "avatar_url",
            "poster_url",
        ]

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        if obj.avatar:
            return obj.avatar.url
        return ""

    def get_poster_url(self, obj):
        request = self.context.get("request")
        if obj.poster and request:
            return request.build_absolute_uri(obj.poster.url)
        if obj.poster:
            return obj.poster.url
        return ""


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "reviewer_name",
            "reviewer_avatar",
            "reviewer_avatar_url",
            "rating",
            "comment",
            "review_date",
        ]

    def get_reviewer_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.reviewer_avatar and request:
            return request.build_absolute_uri(obj.reviewer_avatar.url)
        if obj.reviewer_avatar:
            return obj.reviewer_avatar.url
        return ""


class SaveSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaveSearch
        fields = "__all__"


class PackagePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackagePlan
        fields = "__all__"