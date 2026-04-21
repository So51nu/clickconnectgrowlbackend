from django.db import models
from django.utils.text import slugify
from django.utils import timezone


class BlogCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while BlogCategory.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)

    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )

    short_description = models.TextField(blank=True, default="")
    content = models.TextField(blank=True, default="")

    cover_image = models.ImageField(upload_to="blogs/covers/images/", blank=True, null=True)
    cover_video = models.FileField(upload_to="blogs/covers/videos/", blank=True, null=True)

    author_name = models.CharField(max_length=120, blank=True, default="Admin")
    tags = models.CharField(max_length=500, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="published")
    is_featured = models.BooleanField(default=False)

    meta_title = models.CharField(max_length=255, blank=True, default="")
    meta_description = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            count = 1
            while BlogPost.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug

        if not self.meta_title:
            self.meta_title = self.title

        if not self.meta_description:
            self.meta_description = self.short_description[:160]

        if self.status == "published" and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]


class BlogMedia(models.Model):
    MEDIA_TYPE_CHOICES = (
        ("image", "Image"),
        ("video", "Video"),
    )

    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="media_items")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default="image")
    image = models.ImageField(upload_to="blogs/media/images/", blank=True, null=True)
    video = models.FileField(upload_to="blogs/media/videos/", blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True, default="")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.post.title} - {self.media_type}"


class BlogBlock(models.Model):
    BLOCK_TYPE_CHOICES = (
        ("heading", "Heading"),
        ("paragraph", "Paragraph"),
        ("quote", "Quote"),
        ("html", "HTML"),
        ("image", "Image"),
        ("video", "Video"),
    )

    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="blocks")
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPE_CHOICES, default="paragraph")
    heading = models.CharField(max_length=255, blank=True, default="")
    content = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="blogs/blocks/images/", blank=True, null=True)
    video = models.FileField(upload_to="blogs/blocks/videos/", blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.post.title} - {self.block_type}"


class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.post.title}"