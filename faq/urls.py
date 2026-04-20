from django.urls import path
from .views import FAQPageDataView, FAQInquiryCreateView

urlpatterns = [
    path("page-data/", FAQPageDataView.as_view(), name="faq-page-data"),
    path("inquiries/", FAQInquiryCreateView.as_view(), name="faq-inquiry-create"),
]