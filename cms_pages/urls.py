from django.urls import path

from .views import (
    CMSPageAdminDetailAPIView,
    CMSPageAdminListCreateAPIView,
    CMSPageDetailBySlugAPIView,
    CMSPageListAPIView,
)

urlpatterns = [
    # Custom admin dashboard APIs. Keep these above the slug route.
    path("admin/pages/", CMSPageAdminListCreateAPIView.as_view(), name="cms-page-admin-list-create"),
    path("admin/pages/<int:pk>/", CMSPageAdminDetailAPIView.as_view(), name="cms-page-admin-detail"),

    # Public APIs.
    path("", CMSPageListAPIView.as_view(), name="cms-page-list"),
    path("<slug:cms_slug>/", CMSPageDetailBySlugAPIView.as_view(), name="cms-page-detail-by-slug"),
]
