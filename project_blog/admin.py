from django.contrib import admin
from .models import BlogCategory, BlogPost, BlogMedia, BlogBlock, BlogComment


class BlogMediaInline(admin.TabularInline):
    model = BlogMedia
    extra = 1
    fields = ("media_type", "image", "video", "caption", "sort_order")


class BlogBlockInline(admin.TabularInline):
    model = BlogBlock
    extra = 1
    fields = ("block_type", "heading", "content", "image", "video", "sort_order")


class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 0
    fields = ("name", "email", "message", "is_approved", "created_at")
    readonly_fields = ("created_at",)


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "author_name",
        "status",
        "is_featured",
        "created_at",
    )
    list_filter = ("status", "is_featured", "category", "created_at")
    search_fields = ("title", "slug", "short_description", "content", "author_name")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [BlogMediaInline, BlogBlockInline, BlogCommentInline]


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "name", "email", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("name", "email", "message", "post__title")