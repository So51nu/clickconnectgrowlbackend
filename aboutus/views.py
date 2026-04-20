from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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

from .serializers import (
    AboutHeroSectionSerializer,
    AboutLocationInfoSerializer,
    AboutContactInfoSerializer,
    WhyChooseUsSectionSerializer,
    WhyChooseUsCardSerializer,
    AboutResourceSectionSerializer,
    AboutResourceItemSerializer,
    AboutTeamIntroSectionSerializer,
    AboutTeamSectionSerializer,
    AboutTeamMemberSerializer,
    AboutGallerySectionSerializer,
    AboutGalleryImageSerializer,
)


class AboutPageDataView(APIView):
    def get(self, request, *args, **kwargs):
        hero = AboutHeroSection.objects.filter(is_active=True).first()
        locations = AboutLocationInfo.objects.filter(is_active=True).order_by("order", "id")
        contacts = AboutContactInfo.objects.filter(is_active=True).order_by("order", "id")

        why_choose_section = WhyChooseUsSection.objects.filter(is_active=True).first()
        why_choose_cards = WhyChooseUsCard.objects.filter(is_active=True).order_by("order", "id")

        resource_section = AboutResourceSection.objects.filter(is_active=True).first()
        resource_items = AboutResourceItem.objects.filter(is_active=True).order_by("order", "id")

        team_intro_section = AboutTeamIntroSection.objects.filter(is_active=True).first()
        team_section = AboutTeamSection.objects.filter(is_active=True).first()
        team_members = AboutTeamMember.objects.filter(is_active=True).order_by("order", "id")

        gallery_section = AboutGallerySection.objects.filter(is_active=True).first()
        gallery_images = AboutGalleryImage.objects.filter(is_active=True).order_by("row_number", "order", "id")

        row1 = gallery_images.filter(row_number=1)
        row2 = gallery_images.filter(row_number=2)
        row3 = gallery_images.filter(row_number=3)

        data = {
            "success": True,
            "hero_section": AboutHeroSectionSerializer(hero, context={"request": request}).data if hero else None,
            "location_infos": AboutLocationInfoSerializer(locations, many=True).data,
            "contact_infos": AboutContactInfoSerializer(contacts, many=True).data,

            "why_choose_section": WhyChooseUsSectionSerializer(why_choose_section).data if why_choose_section else None,
            "why_choose_cards": WhyChooseUsCardSerializer(why_choose_cards, many=True).data,

            "resource_section": AboutResourceSectionSerializer(resource_section, context={"request": request}).data if resource_section else None,
            "resource_items": AboutResourceItemSerializer(resource_items, many=True).data,

            "team_intro_section": AboutTeamIntroSectionSerializer(team_intro_section, context={"request": request}).data if team_intro_section else None,
            "team_section": AboutTeamSectionSerializer(team_section).data if team_section else None,
            "team_members": AboutTeamMemberSerializer(team_members, many=True, context={"request": request}).data,

            "gallery_section": AboutGallerySectionSerializer(gallery_section).data if gallery_section else None,
            "gallery_row_1": AboutGalleryImageSerializer(row1, many=True, context={"request": request}).data,
            "gallery_row_2": AboutGalleryImageSerializer(row2, many=True, context={"request": request}).data,
            "gallery_row_3": AboutGalleryImageSerializer(row3, many=True, context={"request": request}).data,
        }

        return Response(data, status=status.HTTP_200_OK)