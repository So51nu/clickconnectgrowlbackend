from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import BlogPost, BlogCategory, BlogComment
from .serializers import (
    BlogPostListSerializer,
    BlogPostDetailSerializer,
    BlogCategorySerializer,
    BlogCommentSerializer,
)


@api_view(["GET"])
def blog_list(request):
    search = request.GET.get("search", "").strip()
    category_slug = request.GET.get("category", "").strip()
    featured = request.GET.get("featured", "").strip()

    qs = BlogPost.objects.filter(status="published").order_by("-created_at")

    if search:
        qs = qs.filter(
            Q(title__icontains=search)
            | Q(short_description__icontains=search)
            | Q(content__icontains=search)
            | Q(author_name__icontains=search)
        )

    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    if featured == "1":
        qs = qs.filter(is_featured=True)

    serializer = BlogPostListSerializer(qs, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def blog_detail(request, slug):
    try:
        post = BlogPost.objects.get(slug=slug, status="published")
    except BlogPost.DoesNotExist:
        return Response({"detail": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = BlogPostDetailSerializer(post, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def blog_categories(request):
    qs = BlogCategory.objects.filter(is_active=True).order_by("name")
    serializer = BlogCategorySerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def related_blogs(request, slug):
    try:
        post = BlogPost.objects.select_related("category").get(slug=slug, status="published")
    except BlogPost.DoesNotExist:
        return Response([], status=status.HTTP_200_OK)

    qs = BlogPost.objects.filter(status="published").exclude(slug=slug)

    if post.category_id:
        qs = qs.filter(category=post.category)

    qs = qs.order_by("-created_at")[:6]

    serializer = BlogPostListSerializer(qs, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET", "POST"])
def blog_comments(request, slug):
    try:
        post = BlogPost.objects.get(slug=slug, status="published")
    except BlogPost.DoesNotExist:
        return Response({"detail": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        comments = post.comments.filter(is_approved=True)
        serializer = BlogCommentSerializer(comments, many=True)
        return Response(serializer.data)

    serializer = BlogCommentSerializer(data=request.data)
    if serializer.is_valid():
        BlogComment.objects.create(
            post=post,
            name=serializer.validated_data["name"],
            email=serializer.validated_data["email"],
            message=serializer.validated_data["message"],
            is_approved=True,
        )
        return Response({"detail": "Comment posted successfully"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)