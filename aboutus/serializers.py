from rest_framework import serializers
from .models import (
    AboutHeroSection,
    AboutLocationInfo,
    AboutContactInfo,
    WhyChooseUsSection,
    WhyChooseUsCard,
    AboutResourceSection,
    AboutResourceItem,
    AboutTeamIntroSection,
    AboutTeamSection,
    AboutTeamMember,
    AboutGallerySection,
    AboutGalleryImage,
)


class BaseImageUrlSerializer(serializers.ModelSerializer):
    def build_absolute_media_url(self, obj, field_name):
        request = self.context.get("request")
        file_field = getattr(obj, field_name, None)
        if file_field:
            if request:
                return request.build_absolute_uri(file_field.url)
            return file_field.url
        return None


class AboutHeroSectionSerializer(BaseImageUrlSerializer):
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = AboutHeroSection
        fields = [
            "id",
            "subtitle",
            "title",
            "short_description",
            "long_description",
            "main_image",
        ]

    def get_main_image(self, obj):
        return self.build_absolute_media_url(obj, "main_image")


class AboutLocationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutLocationInfo
        fields = ["id", "label", "value", "order"]


class AboutContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutContactInfo
        fields = ["id", "type", "label", "value", "order"]


class WhyChooseUsCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhyChooseUsCard
        fields = ["id", "heading", "description", "order"]


class WhyChooseUsSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhyChooseUsSection
        fields = ["id", "subtitle", "title", "description"]


class AboutResourceSectionSerializer(BaseImageUrlSerializer):
    side_image = serializers.SerializerMethodField()

    class Meta:
        model = AboutResourceSection
        fields = ["id", "subtitle", "title", "description", "side_image"]

    def get_side_image(self, obj):
        return self.build_absolute_media_url(obj, "side_image")


class AboutResourceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutResourceItem
        fields = ["id", "heading", "description", "order"]


class AboutTeamIntroSectionSerializer(BaseImageUrlSerializer):
    side_image = serializers.SerializerMethodField()

    class Meta:
        model = AboutTeamIntroSection
        fields = [
            "id",
            "subtitle",
            "title",
            "paragraph_1",
            "paragraph_2",
            "paragraph_3",
            "paragraph_4",
            "side_image",
        ]

    def get_side_image(self, obj):
        return self.build_absolute_media_url(obj, "side_image")


class AboutTeamSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutTeamSection
        fields = ["id", "subtitle", "title", "description"]


class AboutTeamMemberSerializer(BaseImageUrlSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = AboutTeamMember
        fields = ["id", "name", "title", "designation", "image", "order"]

    def get_image(self, obj):
        return self.build_absolute_media_url(obj, "image")


class AboutGallerySectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutGallerySection
        fields = ["id", "subtitle", "title", "description"]


class AboutGalleryImageSerializer(BaseImageUrlSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = AboutGalleryImage
        fields = ["id", "image", "row_number", "order"]

    def get_image(self, obj):
        return self.build_absolute_media_url(obj, "image")