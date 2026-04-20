from django.db import models
from django.utils.text import slugify


class FAQPageSetting(models.Model):
    section_title = models.CharField(max_length=255, default="Frequently Asked Questions")

    seller_form_title = models.CharField(max_length=255, default="Contact Sellers")
    seller_name = models.CharField(max_length=255, default="Growl Real Estate Seller")
    seller_phone = models.CharField(max_length=20, blank=True, null=True)
    seller_email = models.EmailField(blank=True, null=True)
    seller_image = models.ImageField(upload_to="faq/seller/", blank=True, null=True)

    ad_image = models.ImageField(upload_to="faq/ad/", blank=True, null=True)
    ad_logo = models.ImageField(upload_to="faq/ad/logo/", blank=True, null=True)
    ad_title = models.CharField(
        max_length=255,
        default="We can help you find a local real estate agent"
    )
    ad_description = models.TextField(
        blank=True,
        null=True,
        default="Connect with a trusted agent who knows the market inside out - whether you’re buying or selling."
    )
    ad_button_text = models.CharField(max_length=100, default="Connect with an agent")
    ad_button_link = models.CharField(max_length=255, blank=True, null=True, default="#")

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "FAQ Page Setting"
        verbose_name_plural = "FAQ Page Settings"

    def __str__(self):
        return self.section_title


class FAQCategory(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "FAQ Category"
        verbose_name_plural = "FAQ Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class FAQItem(models.Model):
    category = models.ForeignKey(
        FAQCategory,
        on_delete=models.CASCADE,
        related_name="faqs"
    )
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "FAQ Item"
        verbose_name_plural = "FAQ Items"

    def __str__(self):
        return self.question


class FAQInquiry(models.Model):
    full_name = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "FAQ Inquiry"
        verbose_name_plural = "FAQ Inquiries"

    def __str__(self):
        return self.full_name