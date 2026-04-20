from django.urls import path
from . import views

urlpatterns = [
    path("", views.blog_list, name="blog-list"),
    path("categories/", views.blog_categories, name="blog-categories"),
    path("related/<slug:slug>/", views.related_blogs, name="related-blogs"),
    path("<slug:slug>/comments/", views.blog_comments, name="blog-comments"),
    path("<slug:slug>/", views.blog_detail, name="blog-detail"),
]