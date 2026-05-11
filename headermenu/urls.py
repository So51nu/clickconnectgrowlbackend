from django.urls import path
from .views import HeaderMenuListAPIView

urlpatterns = [
    path("menus/", HeaderMenuListAPIView.as_view(), name="header-menu-list"),
]