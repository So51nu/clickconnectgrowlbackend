from django.db import models


class Testimonial(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150, blank=True, default="")
    description = models.TextField()
    avatar = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    rating = models.PositiveSmallIntegerField(default=5)
    width = models.PositiveIntegerField(default=120)
    height = models.PositiveIntegerField(default=120)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "-id"]

    def __str__(self):
        return self.name