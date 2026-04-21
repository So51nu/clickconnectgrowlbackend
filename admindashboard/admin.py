from django.contrib import admin
from .models import (
    AgentProfile,
    PackagePlan,
    Property,
    PropertyImage,
    PropertyFloorPlan,
    Review,
    SaveSearch,
)


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


class PropertyFloorPlanInline(admin.TabularInline):
    model = PropertyFloorPlan
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("id","title", "property_code", "property_status", "post_status","contact_seller", "price", "is_favorite","is_approved", "posting_date")
    list_filter = ("property_status", "post_status", "property_type", "property_label", "is_favorite","contact_seller","is_approved",)
    search_fields = ("title", "property_code", "full_address","developer_name", "city")
    list_editable = ["post_status", "is_approved"]
    inlines = [PropertyImageInline, PropertyFloorPlanInline]


admin.site.register(PackagePlan)
admin.site.register(Review)
admin.site.register(SaveSearch)
from django.contrib import admin
from .models import PropertyAttachment, PropertyNearbyPlace, PropertyReview

class PropertyAttachmentInline(admin.TabularInline):
    model = PropertyAttachment
    extra = 1

class PropertyNearbyPlaceInline(admin.TabularInline):
    model = PropertyNearbyPlace
    extra = 1

class PropertyReviewInline(admin.TabularInline):
    model = PropertyReview
    extra = 1

from django.contrib import admin
from .models import PropertyInquiry, PropertyReview

class PropertyInquiryInline(admin.TabularInline):
    model = PropertyInquiry
    extra = 0
    readonly_fields = ("inquiry_type", "name", "email", "phone", "message", "created_at")
    can_delete = True

class PropertyReviewInline(admin.TabularInline):
    model = PropertyReview
    extra = 1

# agar PropertyAdmin already hai to usme inlines add karo:
# inlines = [PropertyInquiryInline, PropertyReviewInline]

@admin.register(PropertyInquiry)
class PropertyInquiryAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "seller", "inquiry_type", "name", "email", "phone", "created_at")
    search_fields = ("property__title", "name", "email", "phone", "message")
    list_filter = ("inquiry_type", "created_at")


@admin.register(PropertyReview)
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "name", "rating", "created_at")
    search_fields = ("property__title", "name", "email", "message")
    list_filter = ("rating", "created_at")



from django.contrib import admin
from .models import AgentProfile, Property, PropertyInquiry, PropertyReview

@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "phone", "company", "position")
    search_fields = ("full_name", "email", "phone", "company")