from django.urls import path
from . import views
from .source_manager_views import *
urlpatterns = [
    path("dashboard/", views.dashboard_summary, name="dashboard-summary"),

    path("properties/", views.property_list_create, name="property-list-create"),
    path("properties/<int:pk>/", views.property_detail, name="property-detail"),
    path("properties/<int:pk>/toggle-favorite/", views.property_toggle_favorite, name="property-toggle-favorite"),

    path("favorites/", views.favorite_properties, name="favorite-properties"),
    path("reviews/", views.review_list, name="review-list"),
    path("source-manager/dashboard/", SourceManagerDashboardView.as_view(), name="source-manager-dashboard"),
    path("source-manager/add-property/", SourceManagerPropertyCreateView.as_view(), name="source-manager-add-property"),
    path("source-manager/my-properties/",SourceManagerMyPropertiesView.as_view(),name="source-manager-my-properties",),
    path("save-searches/", views.save_search_list_create, name="save-search-list-create"),
    path("save-searches/<int:pk>/", views.save_search_delete, name="save-search-delete"),
    path("cities/", views.city_directory, name="city-directory"),
    path("developers/", views.developer_directory, name="developer-directory"),
    path("cities/<slug:city_slug>/properties/", views.city_property_list, name="city-property-list"),
    path("developers/<slug:developer_slug>/properties/", views.developer_property_list, name="developer-property-list"),
    path("properties/<int:pk>/contact-seller/", views.property_contact_seller, name="property-contact-seller"),
    path("cities/<slug:city_slug>/developers/<slug:developer_slug>/properties/", views.city_developer_property_list, name="city-developer-property-list"),
    path("profile/", views.profile_detail, name="profile-detail"),
    path("change-password/", views.change_password, name="change-password"),
    path("customer/<int:user_id>/dashboard-summary/", views.customer_dashboard_summary, name="customer-dashboard-summary"),
    path("customer/<int:user_id>/viewed-properties/", views.customer_viewed_properties, name="customer-viewed-properties"),
    path("customer/<int:user_id>/favorite-properties/", views.customer_favorite_properties, name="customer-favorite-properties"),
    path("customer/<int:user_id>/visits/", views.customer_visits, name="customer-visits"),
    path("customer/<int:user_id>/liked-videos/", views.customer_liked_videos, name="customer-liked-videos"),
    path("customer/<int:user_id>/search-history/", views.customer_search_history, name="customer-search-history"),

    path("customer/toggle-favorite/", views.customer_toggle_favorite, name="customer-toggle-favorite"),
    path("customer/add-view/", views.customer_add_view, name="customer-add-view"),
    path("customer/book-visit/", views.customer_book_visit, name="customer-book-visit"),
    path("customer/like-video/", views.customer_like_video, name="customer-like-video"),
    path("customer/save-search/", views.customer_save_search, name="customer-save-search"),
    path("package/", views.package_detail, name="package-detail"),
]