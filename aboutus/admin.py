from django.contrib import admin
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


@admin.register(AboutHeroSection)
class AboutHeroSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active"]


@admin.register(AboutLocationInfo)
class AboutLocationInfoAdmin(admin.ModelAdmin):
    list_display = ["label", "order", "is_active"]
    list_editable = ["order", "is_active"]


@admin.register(AboutContactInfo)
class AboutContactInfoAdmin(admin.ModelAdmin):
    list_display = ["label", "type", "value", "order", "is_active"]
    list_editable = ["order", "is_active"]


@admin.register(WhyChooseUsSection)
class WhyChooseUsSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active"]


@admin.register(WhyChooseUsCard)
class WhyChooseUsCardAdmin(admin.ModelAdmin):
    list_display = ["heading", "order", "is_active"]
    list_editable = ["order", "is_active"]


@admin.register(AboutResourceSection)
class AboutResourceSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active"]


@admin.register(AboutResourceItem)
class AboutResourceItemAdmin(admin.ModelAdmin):
    list_display = ["heading", "order", "is_active"]
    list_editable = ["order", "is_active"]


@admin.register(AboutTeamIntroSection)
class AboutTeamIntroSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active"]


@admin.register(AboutTeamSection)
class AboutTeamSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active"]


@admin.register(AboutTeamMember)
class AboutTeamMemberAdmin(admin.ModelAdmin):
    list_display = ["name", "title", "order", "is_active"]
    list_editable = ["order", "is_active"]


@admin.register(AboutGallerySection)
class AboutGallerySectionAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active"]


@admin.register(AboutGalleryImage)
class AboutGalleryImageAdmin(admin.ModelAdmin):
    list_display = ["id", "row_number", "order", "is_active"]
    list_editable = ["row_number", "order", "is_active"]