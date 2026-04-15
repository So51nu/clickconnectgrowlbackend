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
    list_display = ("title", "property_code", "property_status", "post_status", "price", "is_favorite", "posting_date")
    list_filter = ("property_status", "post_status", "property_type", "property_label", "is_favorite")
    search_fields = ("title", "property_code", "full_address")
    inlines = [PropertyImageInline, PropertyFloorPlanInline]


admin.site.register(AgentProfile)
admin.site.register(PackagePlan)
admin.site.register(Review)
admin.site.register(SaveSearch)