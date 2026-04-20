from rest_framework import serializers
from .models import BlogCategory, BlogPost, BlogMedia, BlogBlock, BlogComment


class BlogCategorySerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogCategory
        fields = ["id", "name", "slug", "posts_count"]

    def get_posts_count(self, obj):
        return obj.posts.filter(status="published").count()


class BlogMediaSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = BlogMedia
        fields = [
            "id",
            "media_type",
            "image_url",
            "video_url",
            "caption",
            "sort_order",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def get_video_url(self, obj):
        request = self.context.get("request")
        if obj.video:
            return request.build_absolute_uri(obj.video.url) if request else obj.video.url
        return None


class BlogBlockSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = BlogBlock
        fields = [
            "id",
            "block_type",
            "heading",
            "content",
            "image_url",
            "video_url",
            "sort_order",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def get_video_url(self, obj):
        request = self.context.get("request")
        if obj.video:
            return request.build_absolute_uri(obj.video.url) if request else obj.video.url
        return None


class BlogCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogComment
        fields = ["id", "name", "email", "message", "created_at"]


class BlogPostListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "slug",
            "category",
            "short_description",
            "image",
            "author_name",
            "status",
            "is_featured",
            "created_at",
            "published_at",
            "comments_count",
        ]

    def get_category(self, obj):
        return obj.category.name if obj.category else ""

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.cover_image:
            return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url

        first_image = obj.media_items.filter(media_type="image").first()
        if first_image and first_image.image:
            return request.build_absolute_uri(first_image.image.url) if request else first_image.image.url

        return None

    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class BlogPostDetailSerializer(serializers.ModelSerializer):
    category = BlogCategorySerializer(read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    cover_video_url = serializers.SerializerMethodField()
    media_items = BlogMediaSerializer(many=True, read_only=True)
    blocks = BlogBlockSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "slug",
            "category",
            "short_description",
            "content",
            "cover_image_url",
            "cover_video_url",
            "media_items",
            "blocks",
            "comments",
            "author_name",
            "status",
            "is_featured",
            "meta_title",
            "meta_description",
            "created_at",
            "updated_at",
            "published_at",
            "tags",
        ]

    def get_cover_image_url(self, obj):
        request = self.context.get("request")
        if obj.cover_image:
            return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url
        return None

    def get_cover_video_url(self, obj):
        request = self.context.get("request")
        if obj.cover_video:
            return request.build_absolute_uri(obj.cover_video.url) if request else obj.cover_video.url
        return None

    def get_comments(self, obj):
        comments = obj.comments.filter(is_approved=True)
        return BlogCommentSerializer(comments, many=True).data

    def get_tags(self, obj):
        return obj.tag_list