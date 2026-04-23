
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



from rest_framework import serializers
from .models import PropertyAttachment, PropertyNearbyPlace, PropertyReview

class PropertyAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = PropertyAttachment
        fields = ["id", "title", "file_url", "file_name"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file:
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None

    def get_file_name(self, obj):
        return obj.file.name.split("/")[-1] if obj.file else ""


class PropertyNearbyPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyNearbyPlace
        fields = ["id", "place_name", "distance"]


class PropertyReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyReview
        fields = ["id", "name", "email", "message", "rating", "created_at"]



from rest_framework import serializers
from .models import PropertyInquiry, PropertyReview, AgentProfile

class SimpleAgentProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = AgentProfile
        fields = ["id", "full_name", "email", "phone", "office_number", "avatar_url"]

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return None
class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    floor_plans = PropertyFloorPlanSerializer(many=True, read_only=True)
    imageSrc = serializers.SerializerMethodField()
    postingDate = serializers.SerializerMethodField()
    expiryDate = serializers.SerializerMethodField()
    contact_seller = SimpleAgentProfileSerializer(read_only=True)
    reviews = PropertyReviewSerializer(many=True, read_only=True)
    attachments = PropertyAttachmentSerializer(many=True, read_only=True)
    nearby_places = PropertyNearbyPlaceSerializer(many=True, read_only=True)
    reviews = PropertyReviewSerializer(many=True, read_only=True)
    fallback_sellers = serializers.SerializerMethodField()
    virtual_tour_image_url = serializers.SerializerMethodField()
    city = serializers.CharField(required=False, allow_blank=True)

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
            "city",
            "city_slug",
            "developer_name",
            "developer_slug",
            "short_location",
            "carpet_area",
            "possession_date",
            "attachments",
            "nearby_places",
            "reviews",
            "virtual_tour_image_url",
            "city",
            "contact_seller",
            "reviews",
            "fallback_sellers",
        ]

    

    def get_fallback_sellers(self, obj):
        request = self.context.get("request")
        agents = AgentProfile.objects.all()[:10]
        data = []
        for agent in agents:
            data.append({
                "id": agent.id,
                "full_name": agent.full_name,
                "email": agent.email,
                "phone": agent.phone or agent.office_number,
                "avatar_url": request.build_absolute_uri(agent.avatar.url) if request and agent.avatar else None,
            })
        return data
    def get_virtual_tour_image_url(self, obj):
        request = self.context.get("request")
        if getattr(obj, "virtual_tour_image", None):
            return request.build_absolute_uri(obj.virtual_tour_image.url) if request else obj.virtual_tour_image.url
        return None

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




class PropertyReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyReview
        fields = ["id", "name", "email", "message", "rating", "created_at"]


class PropertyInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyInquiry
        fields = [
            "id",
            "property",
            "seller",
            "inquiry_type",
            "name",
            "email",
            "phone",
            "message",
            "created_at",
        ]
        read_only_fields = ["created_at"]
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



from .models import (
    CustomerPropertyView,
    CustomerFavorite,
    CustomerVisitBooking,
    CustomerLikedVideo,
    CustomerSearchHistory,
)


class CustomerPropertyCardSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    seller_name = serializers.SerializerMethodField()
    seller_phone = serializers.SerializerMethodField()
    seller_avatar = serializers.SerializerMethodField()
    configuration = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "location",
            "short_location",
            "price",
            "bedrooms",
            "video_url",
            "image",
            "seller_name",
            "seller_phone",
            "seller_avatar",
            "configuration",
            "is_favorite",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        primary = obj.images.filter(is_primary=True).first() or obj.images.first()
        if primary and primary.image:
            return request.build_absolute_uri(primary.image.url) if request else primary.image.url
        return ""

    def get_seller_name(self, obj):
        if obj.contact_seller:
            return obj.contact_seller.full_name
        return ""

    def get_seller_phone(self, obj):
        if obj.contact_seller:
            return obj.contact_seller.phone or obj.contact_seller.office_number
        return ""

    def get_seller_avatar(self, obj):
        request = self.context.get("request")
        if obj.contact_seller and obj.contact_seller.avatar:
            return request.build_absolute_uri(obj.contact_seller.avatar.url) if request else obj.contact_seller.avatar.url
        return ""

    def get_configuration(self, obj):
        configs = []
        if obj.bedrooms:
            configs.append(f"{obj.bedrooms} BHK")
        return ", ".join(configs) if configs else obj.property_type.title()

    def get_is_favorite(self, obj):
        request = self.context.get("request")
        user_id = request.GET.get("user_id") if request else None
        if not user_id:
            return False
        return CustomerFavorite.objects.filter(user_id=user_id, property=obj).exists()


class CustomerVisitBookingSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source="property.title", read_only=True)

    class Meta:
        model = CustomerVisitBooking
        fields = "__all__"


class CustomerSearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSearchHistory
        fields = "__all__"



from .models import CustomerReferral

class CustomerReferralSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source="property.title", read_only=True)

    class Meta:
        model = CustomerReferral
        fields = "__all__"