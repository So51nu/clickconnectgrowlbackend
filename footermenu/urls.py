from django.urls import path
from .views import FooterMenuAPIView

urlpatterns = [
    path("", FooterMenuAPIView.as_view(), name="footer-menu"),
]