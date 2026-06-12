from django.urls import path

from .views import JobApplicationCreateView, JobOpeningListView

urlpatterns = [
    path("openings/", JobOpeningListView.as_view(), name="career-openings"),
    path("apply/", JobApplicationCreateView.as_view(), name="career-apply"),
]
