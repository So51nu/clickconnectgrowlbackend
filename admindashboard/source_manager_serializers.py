from rest_framework import serializers
from .models import (
    Property,
    PropertyImage,
    PropertyFloorPlan,
    PropertyNearbyPlace,
    PropertyAttachment,
)
from django.utils.text import slugify


class PropertyImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ["image", "is_primary"]


class PropertyFloorPlanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyFloorPlan
        fields = [
            "floor_name",
            "floor_price",
            "price_postfix",
            "floor_size",
            "size_postfix",
            "bedrooms",
            "bathrooms",
            "description",
            "floor_image",
        ]


class PropertyNearbyPlaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyNearbyPlace
        fields = ["place_name", "distance"]


class PropertyAttachmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyAttachment
        fields = ["title", "file"]



import json
from django.utils.text import slugify
from rest_framework import serializers

from .models import (
    Property,
    PropertyImage,
    PropertyFloorPlan,
    PropertyNearbyPlace,
    PropertyAttachment,
)


class SourceManagerPropertyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
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
            "expiry_date",
            "city",
            "developer_name",
            "short_location",
            "carpet_area",
            "possession_date",
        ]

    def validate_amenities(self, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return [item.strip() for item in value.split(",") if item.strip()]
        return value

    def create(self, validated_data):
        request = self.context["request"]
        agent_profile = self.context["agent_profile"]

        nearby_places_raw = request.data.get("nearby_places", "[]")
        floor_plans_raw = request.data.get("floor_plans", "[]")
        attachments_titles_raw = request.data.get("attachment_titles", "[]")

        try:
            nearby_places = json.loads(nearby_places_raw) if nearby_places_raw else []
        except Exception:
            nearby_places = []

        try:
            floor_plans = json.loads(floor_plans_raw) if floor_plans_raw else []
        except Exception:
            floor_plans = []

        try:
            attachment_titles = json.loads(attachments_titles_raw) if attachments_titles_raw else []
        except Exception:
            attachment_titles = []

        validated_data["contact_seller"] = agent_profile
        validated_data["post_status"] = "pending"
        validated_data["is_approved"] = False

        city = validated_data.get("city", "")
        developer_name = validated_data.get("developer_name", "")

        if city and not validated_data.get("city_slug"):
            validated_data["city_slug"] = slugify(city)

        if developer_name and not validated_data.get("developer_slug"):
            validated_data["developer_slug"] = slugify(developer_name)

        property_obj = Property.objects.create(**validated_data)

        # multiple property images
        property_images = request.FILES.getlist("images")
        primary_index = request.data.get("primary_image_index")

        for index, image in enumerate(property_images):
            is_primary = str(index) == str(primary_index)
            PropertyImage.objects.create(
                property=property_obj,
                image=image,
                is_primary=is_primary,
            )

        # nearby places
        for place in nearby_places:
            place_name = place.get("place_name", "").strip()
            distance = place.get("distance", "").strip()

            if place_name:
                PropertyNearbyPlace.objects.create(
                    property=property_obj,
                    place_name=place_name,
                    distance=distance,
                )

        # floor plans
        floor_plan_images = request.FILES.getlist("floor_plan_images")

        for index, floor_data in enumerate(floor_plans):
            floor_image = floor_plan_images[index] if index < len(floor_plan_images) else None

            PropertyFloorPlan.objects.create(
                property=property_obj,
                floor_name=floor_data.get("floor_name", ""),
                floor_price=floor_data.get("floor_price", ""),
                price_postfix=floor_data.get("price_postfix", ""),
                floor_size=floor_data.get("floor_size", ""),
                size_postfix=floor_data.get("size_postfix", ""),
                bedrooms=floor_data.get("bedrooms", ""),
                bathrooms=floor_data.get("bathrooms", ""),
                description=floor_data.get("description", ""),
                floor_image=floor_image,
            )

        # brochures / attachments
        attachment_files = request.FILES.getlist("attachments")

        for index, file in enumerate(attachment_files):
            title = ""
            if index < len(attachment_titles):
                title = attachment_titles[index]

            PropertyAttachment.objects.create(
                property=property_obj,
                title=title or getattr(file, "name", "Attachment"),
                file=file,
            )

        return property_obj