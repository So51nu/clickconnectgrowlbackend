from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_summary, name="dashboard-summary"),

    path("properties/", views.property_list_create, name="property-list-create"),
    path("properties/<int:pk>/", views.property_detail, name="property-detail"),
    path("properties/<int:pk>/toggle-favorite/", views.property_toggle_favorite, name="property-toggle-favorite"),

    path("favorites/", views.favorite_properties, name="favorite-properties"),
    path("reviews/", views.review_list, name="review-list"),

    path("save-searches/", views.save_search_list_create, name="save-search-list-create"),
    path("save-searches/<int:pk>/", views.save_search_delete, name="save-search-delete"),

    path("profile/", views.profile_detail, name="profile-detail"),
    path("change-password/", views.change_password, name="change-password"),

    path("package/", views.package_detail, name="package-detail"),
]