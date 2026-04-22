from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class AgentProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="agent_profile", null=True, blank=True
    )
    full_name = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    company = models.CharField(max_length=255, blank=True, default="")
    position = models.CharField(max_length=255, blank=True, default="")
    office_number = models.CharField(max_length=50, blank=True, default="")
    office_address = models.CharField(max_length=255, blank=True, default="")
    job = models.CharField(max_length=100, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="")
    facebook = models.CharField(max_length=255, blank=True, default="#")
    twitter = models.CharField(max_length=255, blank=True, default="#")
    linkedin = models.CharField(max_length=255, blank=True, default="#")
    avatar = models.ImageField(upload_to="profile/avatar/", blank=True, null=True)
    poster = models.ImageField(upload_to="profile/poster/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or self.email or "Agent Profile"


class PackagePlan(models.Model):
    title = models.CharField(max_length=100)
    sub_title = models.CharField(max_length=255, blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration = models.CharField(max_length=50, default="month")
    description = models.TextField(blank=True, default="")
    listing_limit = models.PositiveIntegerField(default=50)
    support_24_7 = models.BooleanField(default=True)
    quick_access = models.BooleanField(default=True)
    auto_refresh_ads = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Property(models.Model):
    STATUS_CHOICES = [
        ("publish", "Publish"),
        ("pending", "Pending"),
        ("hidden", "Hidden"),
        ("sold", "Sold"),
    ]

    PROPERTY_TYPE_CHOICES = [
        ("apartment", "Apartment"),
        ("villa", "Villa"),
        ("studio", "Studio"),
        ("office", "Office"),
    ]

    LISTING_TYPE_CHOICES = [
        ("for-rent", "For Rent"),
        ("for-sale", "For Sale"),
    ]

    LABEL_CHOICES = [
        ("new-listing", "New Listing"),
        ("open-house", "Open House"),
        ("featured", "Featured"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    full_address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=20, blank=True, default="")
    country = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=100, blank=True, default="")
    neighborhood = models.CharField(max_length=100, blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="")
    map_embed_url = models.TextField(blank=True, default="")
    contact_seller = models.ForeignKey(
    "AgentProfile",
    related_name="assigned_properties",
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )
    price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    unit_price = models.CharField(max_length=50, blank=True, default="")
    before_price_label = models.CharField(max_length=100, blank=True, default="")
    after_price_label = models.CharField(max_length=100, blank=True, default="")

    property_type = models.CharField(max_length=30, choices=PROPERTY_TYPE_CHOICES, default="apartment")
    property_status = models.CharField(max_length=30, choices=LISTING_TYPE_CHOICES, default="for-sale")
    property_label = models.CharField(max_length=30, choices=LABEL_CHOICES, default="new-listing")
    post_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="publish")

    size_sqft = models.PositiveIntegerField(default=0)
    land_area_sqft = models.PositiveIntegerField(default=0)
    property_code = models.CharField(max_length=100, unique=True)
    rooms = models.PositiveIntegerField(default=0)
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    garages = models.PositiveIntegerField(default=0)
    garages_size_sqft = models.PositiveIntegerField(default=0)
    year_built = models.PositiveIntegerField(default=2024)

    amenities = models.JSONField(default=list, blank=True)
    virtual_tour_type = models.CharField(max_length=50, blank=True, default="")
    virtual_tour_embed_code = models.TextField(blank=True, default="")
    video_url = models.TextField(blank=True, default="")

    is_favorite = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    posting_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=120, blank=True, default="")
    city_slug = models.SlugField(max_length=150, blank=True, default="")
    developer_name = models.CharField(max_length=180, blank=True, default="")
    developer_slug = models.SlugField(max_length=200, blank=True, default="")
    short_location = models.CharField(max_length=180, blank=True, default="")
    carpet_area = models.CharField(max_length=100, blank=True, default="")
    possession_date = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.city and not self.city_slug:
            self.city_slug = slugify(self.city)
        if self.developer_name and not self.developer_slug:
            self.developer_slug = slugify(self.developer_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


from django.db import models
class PropertyAttachment(models.Model):
    property = models.ForeignKey("Property", related_name="attachments", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, default="")
    file = models.FileField(upload_to="properties/attachments/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or self.file.name


class PropertyNearbyPlace(models.Model):
    property = models.ForeignKey("Property", related_name="nearby_places", on_delete=models.CASCADE)
    place_name = models.CharField(max_length=150)
    distance = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return f"{self.place_name} - {self.distance}"


class PropertyReview(models.Model):
    property = models.ForeignKey("Property", related_name="reviews", on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, default="")
    message = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.property.title}"
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="properties/images/")
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.property.title} - Image"


class PropertyFloorPlan(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="floor_plans")
    floor_name = models.CharField(max_length=100, blank=True, default="")
    floor_price = models.CharField(max_length=100, blank=True, default="")
    price_postfix = models.CharField(max_length=50, blank=True, default="")
    floor_size = models.CharField(max_length=100, blank=True, default="")
    size_postfix = models.CharField(max_length=50, blank=True, default="")
    bedrooms = models.CharField(max_length=20, blank=True, default="")
    bathrooms = models.CharField(max_length=20, blank=True, default="")
    description = models.TextField(blank=True, default="")
    floor_image = models.ImageField(upload_to="properties/floorplans/", blank=True, null=True)

    def __str__(self):
        return f"{self.property.title} - {self.floor_name}"


from django.db import models

class PropertyInquiry(models.Model):
    INQUIRY_TYPE_CHOICES = (
        ("contact_seller", "Contact Seller"),
        ("more_about_property", "More About Property"),
    )

    property = models.ForeignKey("Property", related_name="inquiries", on_delete=models.CASCADE)
    seller = models.ForeignKey("AgentProfile", related_name="property_inquiries", on_delete=models.SET_NULL, null=True, blank=True)

    inquiry_type = models.CharField(max_length=50, choices=INQUIRY_TYPE_CHOICES, default="contact_seller")
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=30, blank=True, default="")
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.property.title}"


class PropertyReview(models.Model):
    property = models.ForeignKey("Property", related_name="reviews", on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, default="")
    message = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.property.title}"
    
class Review(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="property_reviews", null=True, blank=True)
    reviewer_name = models.CharField(max_length=100)
    reviewer_avatar = models.ImageField(upload_to="reviews/avatar/", blank=True, null=True)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reviewer_name


class SaveSearch(models.Model):
    title = models.CharField(max_length=100)
    parameters = models.JSONField(default=dict, blank=True)
    email = models.EmailField()
    published_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title 
    



from django.conf import settings


class CustomerPropertyView(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_property_views"
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="customer_views"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "property")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} viewed {self.property.title}"


class CustomerFavorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_favorites"
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="customer_favorites"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "property")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} favorite {self.property.title}"


class CustomerVisitBooking(models.Model):
    STATUS_CHOICES = (
        ("upcoming", "Upcoming"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_visit_bookings"
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="customer_visit_bookings"
    )
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    visit_date = models.DateField()
    visit_time = models.TimeField()
    message = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="upcoming")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.property.title} - {self.visit_date}"


class CustomerLikedVideo(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_liked_videos"
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="customer_liked_videos"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "property")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} liked video {self.property.title}"


class CustomerSearchHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_search_history"
    )
    title = models.CharField(max_length=255)
    parameters = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} searched {self.title}"