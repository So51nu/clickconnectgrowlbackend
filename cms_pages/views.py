from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import CMSPage
from .serializers import CMSPageAdminSerializer, CMSPagePublicSerializer


class CMSPageListAPIView(generics.ListAPIView):
    """Public API: list only published CMS pages."""

    serializer_class = CMSPagePublicSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return CMSPage.objects.filter(status="published").order_by("sort_order", "title")


class CMSPageDetailBySlugAPIView(generics.RetrieveAPIView):
    """Public API: get a published CMS page by slug."""

    serializer_class = CMSPagePublicSerializer
    permission_classes = [permissions.AllowAny]
    lookup_url_kwarg = "cms_slug"

    def get_queryset(self):
        return CMSPage.objects.filter(status="published")

    def get_object(self):
        cms_slug = self.kwargs.get(self.lookup_url_kwarg)
        try:
            return self.get_queryset().get(slug=cms_slug)
        except CMSPage.DoesNotExist:
            raise NotFound("CMS page not found or not published.")


class CMSPageAdminListCreateAPIView(generics.ListCreateAPIView):
    """
    Admin API for custom dashboard.
    Django admin users can also manage pages from /admin/.
    """

    queryset = CMSPage.objects.all().order_by("sort_order", "title")
    serializer_class = CMSPageAdminSerializer
    permission_classes = [permissions.IsAdminUser]


class CMSPageAdminDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CMSPage.objects.all().order_by("sort_order", "title")
    serializer_class = CMSPageAdminSerializer
    permission_classes = [permissions.IsAdminUser]
