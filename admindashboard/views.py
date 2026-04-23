# from datetime import timedelta
# from django.utils import timezone
# from django.db.models import Q
# from rest_framework.decorators import api_view, parser_classes
# from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
# from rest_framework.response import Response
# from rest_framework import status

# from .models import (
#     AgentProfile,
#     PackagePlan,
#     Property,
#     PropertyImage,
#     PropertyFloorPlan,
#     Review,
#     SaveSearch,
# )
# from .serializers import (
#     AgentProfileSerializer,
#     PackagePlanSerializer,
#     PropertySerializer,
#     ReviewSerializer,
#     SaveSearchSerializer,
# )


# def get_or_create_default_profile():
#     profile = AgentProfile.objects.first()
#     if not profile:
#         profile = AgentProfile.objects.create(
#             full_name="Demo Agent",
#             company="Your Company",
#             position="Agent",
#             office_number="1332565894",
#             office_address="10 Bringhurst St, Houston, TX",
#             job="Realtor",
#             email="themeflat@gmail.com",
#             phone="1332565894",
#             location="634 E 236th St, Bronx, NY 10466",
#             facebook="#",
#             twitter="#",
#             linkedin="#",
#         )
#     return profile


# @api_view(["GET"])
# def dashboard_summary(request):
#     total_listing = Property.objects.count()
#     pending = Property.objects.filter(post_status="pending").count()
#     favorites = Property.objects.filter(is_favorite=True).count()
#     reviews_count = Review.objects.count()

#     recent_favorites = Property.objects.filter(is_favorite=True).order_by("-id")[:5]
#     recent_reviews = Review.objects.order_by("-review_date")[:5]

#     monthly_data = []
#     for month in range(1, 13):
#         count = Property.objects.filter(created_at__month=month).count()
#         monthly_data.append(count)

#     return Response({
#         "stats": {
#             "total_listing": total_listing,
#             "remaining": max(0, 50 - total_listing),
#             "pending": pending,
#             "favorites": favorites,
#             "reviews": reviews_count,
#         },
#         "chart": {
#             "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
#             "values": monthly_data,
#         },
#         "favorites": PropertySerializer(recent_favorites, many=True, context={"request": request}).data,
#         "reviews": ReviewSerializer(recent_reviews, many=True, context={"request": request}).data,
#     })

# @api_view(["GET", "POST"])
# @parser_classes([MultiPartParser, FormParser, JSONParser])
# def property_list_create(request):
#     if request.method == "GET":
#         search = request.GET.get("search", "").strip()
#         post_status = request.GET.get("post_status", "").strip()
#         only_favorites = request.GET.get("favorites", "").strip()

#         qs = Property.objects.all().order_by("-id")

#         if search:
#             qs = qs.filter(
#                 Q(title__icontains=search)
#                 | Q(full_address__icontains=search)
#                 | Q(property_code__icontains=search)
#             )

#         if post_status and post_status != "Select":
#             qs = qs.filter(post_status=post_status.lower())

#         if only_favorites == "1":
#             qs = qs.filter(is_favorite=True)

#         return Response(PropertySerializer(qs, many=True, context={"request": request}).data)

#     data = request.data

#     import json

#     amenities_raw = data.get("amenities", "[]")
#     try:
#         amenities_value = json.loads(amenities_raw) if amenities_raw else []
#         if not isinstance(amenities_value, list):
#             amenities_value = []
#     except json.JSONDecodeError:
#         amenities_value = []

#     property_obj = Property.objects.create(
#         title=data.get("title", ""),
#         description=data.get("description", ""),
#         full_address=data.get("full_address", ""),
#         zip_code=data.get("zip_code", ""),
#         country=data.get("country", ""),
#         state=data.get("state", ""),
#         neighborhood=data.get("neighborhood", ""),
#         location=data.get("location", ""),
#         map_embed_url=data.get("map_embed_url", ""),
#         price=data.get("price") or 0,
#         unit_price=data.get("unit_price", ""),
#         before_price_label=data.get("before_price_label", ""),
#         after_price_label=data.get("after_price_label", ""),
#         property_type=data.get("property_type", "apartment"),
#         property_status=data.get("property_status", "for-sale"),
#         property_label=data.get("property_label", "new-listing"),
#         post_status=data.get("post_status", "publish"),
#         size_sqft=data.get("size_sqft") or 0,
#         land_area_sqft=data.get("land_area_sqft") or 0,
#         property_code=data.get("property_code", f"PROP-{timezone.now().strftime('%Y%m%d%H%M%S')}"),
#         rooms=data.get("rooms") or 0,
#         bedrooms=data.get("bedrooms") or 0,
#         bathrooms=data.get("bathrooms") or 0,
#         garages=data.get("garages") or 0,
#         garages_size_sqft=data.get("garages_size_sqft") or 0,
#         year_built=data.get("year_built") or 2024,
#         amenities=amenities_value,
#         virtual_tour_type=data.get("virtual_tour_type", ""),
#         virtual_tour_embed_code=data.get("virtual_tour_embed_code", ""),
#         video_url=data.get("video_url", ""),
#         is_favorite=str(data.get("is_favorite", "false")).lower() == "true",
#         is_approved=str(data.get("is_approved", "true")).lower() == "true",
#         expiry_date=timezone.now().date() + timedelta(days=30),
#     )

#     images = request.FILES.getlist("images")
#     for index, img in enumerate(images):
#         PropertyImage.objects.create(
#             property=property_obj,
#             image=img,
#             is_primary=(index == 0),
#         )

#     # floor plans save
#     index = 0
#     while True:
#         floor_name = request.data.get(f"floor_plans[{index}][floor_name]")
#         floor_price = request.data.get(f"floor_plans[{index}][floor_price]")
#         price_postfix = request.data.get(f"floor_plans[{index}][price_postfix]")
#         floor_size = request.data.get(f"floor_plans[{index}][floor_size]")
#         size_postfix = request.data.get(f"floor_plans[{index}][size_postfix]")
#         bedrooms = request.data.get(f"floor_plans[{index}][bedrooms]")
#         bathrooms = request.data.get(f"floor_plans[{index}][bathrooms]")
#         description = request.data.get(f"floor_plans[{index}][description]")
#         floor_image = request.FILES.get(f"floor_plans[{index}][floor_image]")

#         if (
#             floor_name is None
#             and floor_price is None
#             and floor_size is None
#             and bedrooms is None
#             and bathrooms is None
#             and description is None
#             and floor_image is None
#         ):
#             break

#         PropertyFloorPlan.objects.create(
#             property=property_obj,
#             floor_name=floor_name or "",
#             floor_price=floor_price or "",
#             price_postfix=price_postfix or "",
#             floor_size=floor_size or "",
#             size_postfix=size_postfix or "",
#             bedrooms=bedrooms or "",
#             bathrooms=bathrooms or "",
#             description=description or "",
#             floor_image=floor_image,
#         )

#         index += 1
#     response_data = PropertySerializer(property_obj, context={"request": request}).data
#     return Response(response_data, status=status.HTTP_201_CREATED)

# @api_view(["GET", "PUT", "DELETE"])
# @parser_classes([MultiPartParser, FormParser, JSONParser])
# def property_detail(request, pk):
#     try:
#         property_obj = Property.objects.get(pk=pk)
#     except Property.DoesNotExist:
#         return Response({"detail": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

#     if request.method == "GET":
#         return Response(PropertySerializer(property_obj, context={"request": request}).data)

#     if request.method == "PUT":
#         data = request.data

#         for field in [
#             "title", "description", "full_address", "zip_code", "country", "state",
#             "neighborhood", "location", "map_embed_url", "unit_price",
#             "before_price_label", "after_price_label", "property_type",
#             "property_status", "property_label", "post_status",
#             "virtual_tour_type", "virtual_tour_embed_code", "video_url"
#         ]:
#             if field in data:
#                 setattr(property_obj, field, data.get(field))

#         for num_field in [
#             "price", "size_sqft", "land_area_sqft", "rooms", "bedrooms",
#             "bathrooms", "garages", "garages_size_sqft", "year_built"
#         ]:
#             if num_field in data:
#                 value = data.get(num_field)
#                 setattr(property_obj, num_field, value or 0)

#         if "property_code" in data:
#             property_obj.property_code = data.get("property_code")

#         if hasattr(request.data, "getlist") and "amenities" in request.data:
#             property_obj.amenities = request.data.getlist("amenities")

#         property_obj.save()

#         images = request.FILES.getlist("images")
#         if images:
#             property_obj.images.all().delete()
#             for index, img in enumerate(images):
#                 PropertyImage.objects.create(
#                     property=property_obj,
#                     image=img,
#                     is_primary=(index == 0),
#                 )

#         return Response(PropertySerializer(property_obj, context={"request": request}).data)

#     property_obj.delete()
#     return Response({"detail": "Property deleted successfully"})
    

# @api_view(["POST"])
# def property_toggle_favorite(request, pk):
#     try:
#         property_obj = Property.objects.get(pk=pk)
#     except Property.DoesNotExist:
#         return Response({"detail": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

#     property_obj.is_favorite = not property_obj.is_favorite
#     property_obj.save()
#     return Response({
#         "id": property_obj.id,
#         "is_favorite": property_obj.is_favorite,
#         "message": "Favorite updated successfully"
#     })


# @api_view(["GET"])
# def favorite_properties(request):
#     qs = Property.objects.filter(is_favorite=True).order_by("-id")
#     return Response(PropertySerializer(qs, many=True, context={"request": request}).data)


# @api_view(["GET"])
# def review_list(request):
#     qs = Review.objects.order_by("-review_date")
#     return Response(ReviewSerializer(qs, many=True, context={"request": request}).data)


# @api_view(["GET", "POST"])
# def save_search_list_create(request):
#     if request.method == "GET":
#         searches = SaveSearch.objects.order_by("-published_at")
#         return Response(SaveSearchSerializer(searches, many=True).data)

#     serializer = SaveSearchSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["DELETE"])
# def save_search_delete(request, pk):
#     try:
#         obj = SaveSearch.objects.get(pk=pk)
#     except SaveSearch.DoesNotExist:
#         return Response({"detail": "Save search not found"}, status=status.HTTP_404_NOT_FOUND)

#     obj.delete()
#     return Response({"detail": "Deleted successfully"})


# @api_view(["GET", "PUT"])
# @parser_classes([MultiPartParser, FormParser, JSONParser])
# def profile_detail(request):
#     profile = get_or_create_default_profile()

#     if request.method == "GET":
#         return Response(AgentProfileSerializer(profile, context={"request": request}).data)

#     for field in [
#         "full_name", "description", "company", "position", "office_number",
#         "office_address", "job", "email", "phone", "location",
#         "facebook", "twitter", "linkedin"
#     ]:
#         if field in request.data:
#             setattr(profile, field, request.data.get(field))

#     if request.FILES.get("avatar"):
#         profile.avatar = request.FILES.get("avatar")

#     if request.FILES.get("poster"):
#         profile.poster = request.FILES.get("poster")

#     profile.save()
#     return Response(AgentProfileSerializer(profile, context={"request": request}).data)


# @api_view(["POST"])
# def change_password(request):
#     old_password = request.data.get("old_password", "")
#     new_password = request.data.get("new_password", "")
#     confirm_password = request.data.get("confirm_password", "")

#     if not old_password or not new_password or not confirm_password:
#         return Response({"detail": "All password fields are required"}, status=status.HTTP_400_BAD_REQUEST)

#     if new_password != confirm_password:
#         return Response({"detail": "New password and confirm password do not match"}, status=status.HTTP_400_BAD_REQUEST)

#     return Response({"detail": "Password updated successfully"})


# @api_view(["GET"])
# def package_detail(request):
#     package = PackagePlan.objects.filter(is_active=True).first()
#     if not package:
#         package = PackagePlan.objects.create(
#             title="Basic",
#             sub_title="Automatically reach potential customers",
#             price=19,
#             duration="month",
#             description="Per month, per company or team members",
#             listing_limit=50,
#             support_24_7=True,
#             quick_access=True,
#             auto_refresh_ads=True,
#             is_active=True,
#         )
#     return Response(PackagePlanSerializer(package).data)

from datetime import timedelta
import json

from django.utils import timezone
from django.db.models import Q
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .models import PropertyInquiry, PropertyReview
from .serializers import PropertyInquirySerializer
from .models import (
    AgentProfile,
    PackagePlan,
    Property,
    PropertyImage,
    PropertyFloorPlan,
    Review,
    SaveSearch,
)
from .serializers import (
    AgentProfileSerializer,
    PackagePlanSerializer,
    PropertySerializer,
    ReviewSerializer,
    SaveSearchSerializer,
)


def get_or_create_default_profile():
    profile = AgentProfile.objects.first()
    if not profile:
        profile = AgentProfile.objects.create(
            full_name="Demo Agent",
            company="Your Company",
            position="Agent",
            office_number="1332565894",
            office_address="10 Bringhurst St, Houston, TX",
            job="Realtor",
            email="themeflat@gmail.com",
            phone="1332565894",
            location="634 E 236th St, Bronx, NY 10466",
            facebook="#",
            twitter="#",
            linkedin="#",
        )
    return profile


def parse_amenities(data):
    amenities_raw = data.get("amenities", "[]")
    try:
        amenities_value = json.loads(amenities_raw) if amenities_raw else []
        if not isinstance(amenities_value, list):
            return []
        return amenities_value
    except (json.JSONDecodeError, TypeError):
        return []


def parse_bool(value, default=False):
    if value is None:
        return default
    return str(value).lower() == "true"


def save_floor_plans_from_request(property_obj, request):
    floor_index = 0
    while True:
        floor_name = request.data.get(f"floor_plans[{floor_index}][floor_name]")
        floor_price = request.data.get(f"floor_plans[{floor_index}][floor_price]")
        price_postfix = request.data.get(f"floor_plans[{floor_index}][price_postfix]")
        floor_size = request.data.get(f"floor_plans[{floor_index}][floor_size]")
        size_postfix = request.data.get(f"floor_plans[{floor_index}][size_postfix]")
        bedrooms = request.data.get(f"floor_plans[{floor_index}][bedrooms]")
        bathrooms = request.data.get(f"floor_plans[{floor_index}][bathrooms]")
        description = request.data.get(f"floor_plans[{floor_index}][description]")
        floor_image = request.FILES.get(f"floor_plans[{floor_index}][floor_image]")

        if (
            floor_name is None
            and floor_price is None
            and price_postfix is None
            and floor_size is None
            and size_postfix is None
            and bedrooms is None
            and bathrooms is None
            and description is None
            and floor_image is None
        ):
            break

        PropertyFloorPlan.objects.create(
            property=property_obj,
            floor_name=floor_name or "",
            floor_price=floor_price or "",
            price_postfix=price_postfix or "",
            floor_size=floor_size or "",
            size_postfix=size_postfix or "",
            bedrooms=bedrooms or "",
            bathrooms=bathrooms or "",
            description=description or "",
            floor_image=floor_image,
        )
        floor_index += 1


@api_view(["GET"])
def dashboard_summary(request):
    total_listing = Property.objects.count()
    pending = Property.objects.filter(post_status="pending").count()
    favorites = Property.objects.filter(is_favorite=True).count()
    reviews_count = Review.objects.count()

    recent_favorites = Property.objects.filter(is_favorite=True).order_by("-id")[:5]
    recent_reviews = Review.objects.order_by("-review_date")[:5]

    monthly_data = []
    for month in range(1, 13):
        count = Property.objects.filter(created_at__month=month).count()
        monthly_data.append(count)

    return Response({
        "stats": {
            "total_listing": total_listing,
            "remaining": max(0, 50 - total_listing),
            "pending": pending,
            "favorites": favorites,
            "reviews": reviews_count,
        },
        "chart": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "values": monthly_data,
        },
        "favorites": PropertySerializer(recent_favorites, many=True, context={"request": request}).data,
        "reviews": ReviewSerializer(recent_reviews, many=True, context={"request": request}).data,
    })


@api_view(["GET", "POST"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def property_list_create(request):
    if request.method == "GET":
        search = request.GET.get("search", "").strip()
        post_status = request.GET.get("post_status", "").strip()
        only_favorites = request.GET.get("favorites", "").strip()

        qs = Property.objects.all().order_by("-id")

        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(full_address__icontains=search)
                | Q(property_code__icontains=search)
            )

        if post_status and post_status != "Select":
            qs = qs.filter(post_status=post_status.lower())

        if only_favorites == "1":
            qs = qs.filter(is_favorite=True)

        return Response(PropertySerializer(qs, many=True, context={"request": request}).data)

    data = request.data
    amenities_value = parse_amenities(data)

    property_obj = Property.objects.create(
        title=data.get("title", ""),
        description=data.get("description", ""),
        full_address=data.get("full_address", ""),
        zip_code=data.get("zip_code", ""),
        country=data.get("country", ""),
        state=data.get("state", ""),
        neighborhood=data.get("neighborhood", ""),
        location=data.get("location", ""),
        map_embed_url=data.get("map_embed_url", ""),
        price=data.get("price") or 0,
        unit_price=data.get("unit_price", ""),
        before_price_label=data.get("before_price_label", ""),
        after_price_label=data.get("after_price_label", ""),
        property_type=data.get("property_type", "apartment"),
        property_status=data.get("property_status", "for-sale"),
        property_label=data.get("property_label", "new-listing"),
        post_status=data.get("post_status", "publish"),
        size_sqft=data.get("size_sqft") or 0,
        land_area_sqft=data.get("land_area_sqft") or 0,
        property_code=data.get("property_code", f"PROP-{timezone.now().strftime('%Y%m%d%H%M%S')}"),
        rooms=data.get("rooms") or 0,
        bedrooms=data.get("bedrooms") or 0,
        bathrooms=data.get("bathrooms") or 0,
        garages=data.get("garages") or 0,
        garages_size_sqft=data.get("garages_size_sqft") or 0,
        year_built=data.get("year_built") or 2024,
        amenities=amenities_value,
        virtual_tour_type=data.get("virtual_tour_type", ""),
        virtual_tour_embed_code=data.get("virtual_tour_embed_code", ""),
        video_url=data.get("video_url", ""),
        is_favorite=parse_bool(data.get("is_favorite"), False),
        is_approved=parse_bool(data.get("is_approved"), True),
        city=data.get("city", ""),
        city_slug=data.get("city_slug", ""),
        developer_name=data.get("developer_name", ""),
        developer_slug=data.get("developer_slug", ""),
        short_location=data.get("short_location", ""),
        carpet_area=data.get("carpet_area", ""),
        possession_date=data.get("possession_date", ""),
        
        expiry_date=timezone.now().date() + timedelta(days=30),
    )

    images = request.FILES.getlist("images")
    for index, img in enumerate(images):
        PropertyImage.objects.create(
            property=property_obj,
            image=img,
            is_primary=(index == 0),
        )
    

    if request.FILES.get("virtual_tour_image"):
        property_obj.virtual_tour_image = request.FILES.get("virtual_tour_image")

    if request.FILES.get("video_file"):
        property_obj.video_file = request.FILES.get("video_file")

    save_floor_plans_from_request(property_obj, request)

    response_data = PropertySerializer(property_obj, context={"request": request}).data
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def property_detail(request, pk):
    try:
        property_obj = Property.objects.get(pk=pk)
    except Property.DoesNotExist:
        return Response({"detail": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(PropertySerializer(property_obj, context={"request": request}).data)

    if request.method == "PUT":
        data = request.data

        for field in [
            "title",
            "description",
            "full_address",
            "zip_code",
            "country",
            "state",
            "neighborhood",
            "location",
            "map_embed_url",
            "unit_price",
            "before_price_label",
            "after_price_label",
            "property_type",
            "property_status",
            "property_label",
            "post_status",
            "virtual_tour_type",
            "virtual_tour_embed_code",
            "video_url",
            "city",
            "city_slug",
            "developer_name",
            "developer_slug",
            "short_location",
            "carpet_area",
            "possession_date",
        ]:
            if field in data:
                setattr(property_obj, field, data.get(field))

        for num_field in [
            "price",
            "size_sqft",
            "land_area_sqft",
            "rooms",
            "bedrooms",
            "bathrooms",
            "garages",
            "garages_size_sqft",
            "year_built",
        ]:
            if num_field in data:
                setattr(property_obj, num_field, data.get(num_field) or 0)

        if "property_code" in data:
            property_obj.property_code = data.get("property_code")

        if "amenities" in data:
            property_obj.amenities = parse_amenities(data)

        if "is_favorite" in data:
            property_obj.is_favorite = parse_bool(data.get("is_favorite"), property_obj.is_favorite)

        if "is_approved" in data:
            property_obj.is_approved = parse_bool(data.get("is_approved"), property_obj.is_approved)

        property_obj.save()

        images = request.FILES.getlist("images")
        if images:
            property_obj.images.all().delete()
            for index, img in enumerate(images):
                PropertyImage.objects.create(
                    property=property_obj,
                    image=img,
                    is_primary=(index == 0),
                )

        property_obj.floor_plans.all().delete()
        save_floor_plans_from_request(property_obj, request)

        return Response(PropertySerializer(property_obj, context={"request": request}).data)

    property_obj.delete()
    return Response({"detail": "Property deleted successfully"})
from django.core.mail import send_mail
from django.conf import settings

@api_view(["POST"])
def property_contact_seller(request, pk):
    try:
        property_obj = Property.objects.select_related("contact_seller").get(pk=pk)
    except Property.DoesNotExist:
        return Response({"detail": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

    seller = property_obj.contact_seller
    if not seller:
        seller = AgentProfile.objects.first()

    inquiry_type = request.data.get("inquiry_type", "contact_seller")
    name = request.data.get("name", "").strip()
    email = request.data.get("email", "").strip()
    phone = request.data.get("phone", "").strip()
    message = request.data.get("message", "").strip()

    if not name or not message:
        return Response(
            {"detail": "Name and message are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    inquiry = PropertyInquiry.objects.create(
        property=property_obj,
        seller=seller,
        inquiry_type=inquiry_type,
        name=name,
        email=email,
        phone=phone,
        message=message,
    )

    seller_email = seller.email if seller and seller.email else None
    admin_email = getattr(settings, "ADMIN_NOTIFICATION_EMAIL", "")

    recipients = []
    if seller_email:
        recipients.append(seller_email)
    if admin_email:
        recipients.append(admin_email)

    if recipients:
        subject = f"New inquiry for {property_obj.title}"
        body = (
            f"Property: {property_obj.title}\n"
            f"Property ID: {property_obj.property_code}\n"
            f"Inquiry Type: {inquiry_type}\n"
            f"Name: {name}\n"
            f"Email: {email or '-'}\n"
            f"Phone: {phone or '-'}\n"
            f"Assigned Seller: {seller.full_name if seller else '-'}\n\n"
            f"Message:\n{message}\n"
        )

        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                recipients,
                fail_silently=True,
            )
        except Exception:
            pass

    return Response(
        {
            "detail": "Inquiry sent successfully",
            "inquiry_id": inquiry.id,
        },
        status=status.HTTP_201_CREATED,
    )
@api_view(["POST"])
def property_toggle_favorite(request, pk):
    try:
        property_obj = Property.objects.get(pk=pk)
    except Property.DoesNotExist:
        return Response({"detail": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

    property_obj.is_favorite = not property_obj.is_favorite
    property_obj.save()
    return Response({
        "id": property_obj.id,
        "is_favorite": property_obj.is_favorite,
        "message": "Favorite updated successfully"
    })


@api_view(["GET"])
def favorite_properties(request):
    qs = Property.objects.filter(is_favorite=True).order_by("-id")
    return Response(PropertySerializer(qs, many=True, context={"request": request}).data)


@api_view(["GET"])
def review_list(request):
    qs = Review.objects.order_by("-review_date")
    return Response(ReviewSerializer(qs, many=True, context={"request": request}).data)


@api_view(["GET", "POST"])
def save_search_list_create(request):
    if request.method == "GET":
        searches = SaveSearch.objects.order_by("-published_at")
        return Response(SaveSearchSerializer(searches, many=True).data)

    serializer = SaveSearchSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def save_search_delete(request, pk):
    try:
        obj = SaveSearch.objects.get(pk=pk)
    except SaveSearch.DoesNotExist:
        return Response({"detail": "Save search not found"}, status=status.HTTP_404_NOT_FOUND)

    obj.delete()
    return Response({"detail": "Deleted successfully"})



@api_view(["GET"])
def city_property_list(request, city_slug):
    qs = Property.objects.filter(city_slug=city_slug).order_by("-id")
    return Response(PropertySerializer(qs, many=True, context={"request": request}).data)


@api_view(["GET"])
def developer_property_list(request, developer_slug):
    qs = Property.objects.filter(developer_slug=developer_slug).order_by("-id")
    return Response(PropertySerializer(qs, many=True, context={"request": request}).data)


@api_view(["GET"])
def city_developer_property_list(request, city_slug, developer_slug):
    qs = Property.objects.filter(
        city_slug=city_slug,
        developer_slug=developer_slug
    ).order_by("-id")
    return Response(PropertySerializer(qs, many=True, context={"request": request}).data)


@api_view(["GET"])
def developer_directory(request):
    developers = (
        Property.objects.exclude(developer_name="")
        .values("developer_name", "developer_slug", "city", "city_slug")
        .distinct()
        .order_by("developer_name")
    )
    return Response(list(developers))


@api_view(["GET"])
def city_directory(request):
    cities = (
        Property.objects.exclude(city="")
        .values("city", "city_slug")
        .distinct()
        .order_by("city")
    )
    return Response(list(cities))



@api_view(["GET", "PUT"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def profile_detail(request):
    profile = get_or_create_default_profile()

    if request.method == "GET":
        return Response(AgentProfileSerializer(profile, context={"request": request}).data)

    for field in [
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
    ]:
        if field in request.data:
            setattr(profile, field, request.data.get(field))

    if request.FILES.get("avatar"):
        profile.avatar = request.FILES.get("avatar")

    if request.FILES.get("poster"):
        profile.poster = request.FILES.get("poster")

    profile.save()
    return Response(AgentProfileSerializer(profile, context={"request": request}).data)


@api_view(["POST"])
def change_password(request):
    old_password = request.data.get("old_password", "")
    new_password = request.data.get("new_password", "")
    confirm_password = request.data.get("confirm_password", "")

    if not old_password or not new_password or not confirm_password:
        return Response({"detail": "All password fields are required"}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_password:
        return Response({"detail": "New password and confirm password do not match"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail": "Password updated successfully"})


@api_view(["GET"])
def package_detail(request):
    package = PackagePlan.objects.filter(is_active=True).first()
    if not package:
        package = PackagePlan.objects.create(
            title="Basic",
            sub_title="Automatically reach potential customers",
            price=19,
            duration="month",
            description="Per month, per company or team members",
            listing_limit=50,
            support_24_7=True,
            quick_access=True,
            auto_refresh_ads=True,
            is_active=True,
        )
    return Response(PackagePlanSerializer(package).data)



from django.contrib.auth.models import User
from .models import (
    CustomerPropertyView,
    CustomerFavorite,
    CustomerVisitBooking,
    CustomerLikedVideo,
    CustomerSearchHistory,
)
from .serializers import (
    CustomerPropertyCardSerializer,
    CustomerVisitBookingSerializer,
    CustomerSearchHistorySerializer,
)

@api_view(["GET"])
def customer_dashboard_summary(request, user_id):
    return Response({
        "viewed_count": CustomerPropertyView.objects.filter(user_id=user_id).count(),
        "favorite_count": CustomerFavorite.objects.filter(user_id=user_id).count(),
        "visit_count": CustomerVisitBooking.objects.filter(user_id=user_id, status="upcoming").count(),
        "booking_count": CustomerVisitBooking.objects.filter(user_id=user_id).count(),
        "liked_count": CustomerLikedVideo.objects.filter(user_id=user_id).count(),
        "search_count": CustomerSearchHistory.objects.filter(user_id=user_id).count(),
    })


@api_view(["GET"])
def customer_viewed_properties(request, user_id):
    property_ids = CustomerPropertyView.objects.filter(user_id=user_id).values_list("property_id", flat=True)
    qs = Property.objects.filter(id__in=property_ids).order_by("-id")
    serializer = CustomerPropertyCardSerializer(qs, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def customer_favorite_properties(request, user_id):
    property_ids = CustomerFavorite.objects.filter(user_id=user_id).values_list("property_id", flat=True)
    qs = Property.objects.filter(id__in=property_ids).order_by("-id")
    serializer = CustomerPropertyCardSerializer(qs, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["POST"])
def customer_toggle_favorite(request):
    user_id = request.data.get("user_id")
    property_id = request.data.get("property_id")

    if not user_id or not property_id:
        return Response({"success": False, "message": "user_id and property_id required"}, status=400)

    favorite, created = CustomerFavorite.objects.get_or_create(
        user_id=user_id,
        property_id=property_id,
    )

    if created:
        return Response({"success": True, "is_favorite": True, "message": "Added to favorites"})

    favorite.delete()
    return Response({"success": True, "is_favorite": False, "message": "Removed from favorites"})


@api_view(["POST"])
def customer_add_view(request):
    user_id = request.data.get("user_id")
    property_id = request.data.get("property_id")

    if not user_id or not property_id:
        return Response({"success": False, "message": "user_id and property_id required"}, status=400)

    CustomerPropertyView.objects.get_or_create(
        user_id=user_id,
        property_id=property_id,
    )
    return Response({"success": True, "message": "View added"})


@api_view(["POST"])
def customer_book_visit(request):
    serializer = CustomerVisitBookingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"success": True, "message": "Visit booked successfully", "data": serializer.data},
            status=201
        )
    return Response(serializer.errors, status=400)


@api_view(["GET"])
def customer_visits(request, user_id):
    status_filter = request.GET.get("status")
    qs = CustomerVisitBooking.objects.filter(user_id=user_id)

    if status_filter:
        qs = qs.filter(status=status_filter)

    serializer = CustomerVisitBookingSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def customer_like_video(request):
    user_id = request.data.get("user_id")
    property_id = request.data.get("property_id")

    if not user_id or not property_id:
        return Response({"success": False, "message": "user_id and property_id required"}, status=400)

    liked, created = CustomerLikedVideo.objects.get_or_create(
        user_id=user_id,
        property_id=property_id,
    )

    if created:
        return Response({"success": True, "liked": True, "message": "Video liked"})

    liked.delete()
    return Response({"success": True, "liked": False, "message": "Video unliked"})


@api_view(["GET"])
def customer_liked_videos(request, user_id):
    property_ids = CustomerLikedVideo.objects.filter(user_id=user_id).values_list("property_id", flat=True)
    qs = Property.objects.filter(id__in=property_ids).order_by("-id")
    serializer = CustomerPropertyCardSerializer(qs, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["POST"])
def customer_save_search(request):
    serializer = CustomerSearchHistorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["GET"])
def customer_search_history(request, user_id):
    qs = CustomerSearchHistory.objects.filter(user_id=user_id)
    serializer = CustomerSearchHistorySerializer(qs, many=True)
    return Response(serializer.data)



from .models import CustomerReferral
from .serializers import CustomerReferralSerializer

from urllib.parse import quote


@api_view(["POST"])
def create_customer_referrals(request):
    user_id = request.data.get("user_id")
    inviter_name = request.data.get("inviter_name")
    inviter_phone = request.data.get("inviter_phone")
    invitees = request.data.get("invitees", [])

    if not user_id or not inviter_name or not inviter_phone:
        return Response(
            {"success": False, "message": "Inviter details are required."},
            status=400,
        )

    if not invitees or not isinstance(invitees, list):
        return Response(
            {"success": False, "message": "At least one invitee is required."},
            status=400,
        )

    company_name = "Growl Real Estate"
    website_link = "https://growlrealestate.com" # <-- apni live website link yaha daalo

    created_items = []
    whatsapp_links = []

    for item in invitees:
        referral_type = item.get("referral_type")
        project_ids = item.get("project_ids", []) or []
        locations = item.get("locations", []) or []

        invitee_name = item.get("name", "").strip()
        invitee_phone = str(item.get("phone", "")).strip()
        invitee_email = item.get("email", "").strip()
        relation = item.get("relation", "").strip()

        clean_phone = "".join(ch for ch in invitee_phone if ch.isdigit())
        if clean_phone and len(clean_phone) == 10:
            clean_phone = f"91{clean_phone}"

        whatsapp_message = (
            f"Referral\n"
            f"👋 Hi {invitee_name}\n"
            f"You’ve been invited by {inviter_name} to explore properties on {company_name} "
            f"– India’s first consumer centric real-estate buying platform.\n\n"
            f"🏡 Browse verified projects, take a live tour, and even book your dream home – all from your home.\n\n"
            f"Tap below to start exploring 👇\n"
            f"{website_link}\n\n"
            f"(P.S. You’ll get an exclusive discount on your dream home if you book through us!)"
        )

        whatsapp_url = ""
        if clean_phone:
            whatsapp_url = f"https://wa.me/{clean_phone}?text={quote(whatsapp_message)}"

        if referral_type == "project":
            if not project_ids:
                return Response(
                    {"success": False, "message": "Please select at least one project."},
                    status=400,
                )

            for project_id in project_ids:
                referral = CustomerReferral.objects.create(
                    user_id=user_id,
                    inviter_name=inviter_name,
                    inviter_phone=inviter_phone,
                    invitee_name=invitee_name,
                    invitee_phone=invitee_phone,
                    invitee_email=invitee_email,
                    relation=relation,
                    referral_type="project",
                    property_id=project_id,
                    location="",
                )
                created_items.append(referral)

            if whatsapp_url:
                whatsapp_links.append({
                    "name": invitee_name,
                    "phone": invitee_phone,
                    "url": whatsapp_url,
                })

        elif referral_type == "location":
            if not locations:
                return Response(
                    {"success": False, "message": "Please select at least one city."},
                    status=400,
                )

            for city in locations:
                referral = CustomerReferral.objects.create(
                    user_id=user_id,
                    inviter_name=inviter_name,
                    inviter_phone=inviter_phone,
                    invitee_name=invitee_name,
                    invitee_phone=invitee_phone,
                    invitee_email=invitee_email,
                    relation=relation,
                    referral_type="location",
                    property=None,
                    location=city,
                )
                created_items.append(referral)

            if whatsapp_url:
                whatsapp_links.append({
                    "name": invitee_name,
                    "phone": invitee_phone,
                    "url": whatsapp_url,
                })

        else:
            return Response(
                {"success": False, "message": "Invalid referral type."},
                status=400,
            )

    serializer = CustomerReferralSerializer(created_items, many=True)
    return Response(
        {
            "success": True,
            "message": "Referral invite created successfully.",
            "data": serializer.data,
            "whatsapp_links": whatsapp_links,
        },
        status=201,
    )

@api_view(["GET"])
def customer_referrals_list(request, user_id):
    qs = CustomerReferral.objects.filter(user_id=user_id).order_by("-created_at")
    serializer = CustomerReferralSerializer(qs, many=True)
    return Response(serializer.data)