from django.urls import path
from .views import testimonial_list

urlpatterns = [
    path("", testimonial_list, name="testimonial-list"),
]