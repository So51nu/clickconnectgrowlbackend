from django.urls import path
from .views import ContactInquiryCreateView

urlpatterns = [
    path("submit/", ContactInquiryCreateView.as_view(), name="contact-submit"),
]