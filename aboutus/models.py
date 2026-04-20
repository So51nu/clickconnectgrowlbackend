from django.db import models


class AboutHeroSection(models.Model):
    subtitle = models.CharField(max_length=255, default="About Growl Real Estate")
    title = models.CharField(max_length=255, default="Mumbai’s Trusted Property Partners")
    short_description = models.TextField(blank=True, null=True)
    long_description = models.TextField(blank=True, null=True)
    main_image = models.ImageField(upload_to="aboutus/hero/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "About Hero Section"
        verbose_name_plural = "About Hero Section"

    def __str__(self):
        return self.title


class AboutLocationInfo(models.Model):
    label = models.CharField(max_length=255, default="Serving Locations")
    value = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "About Location Info"
        verbose_name_plural = "About Location Info"

    def __str__(self):
        return self.label


class AboutContactInfo(models.Model):
    CONTACT_TYPE_CHOICES = (
        ("phone", "Phone"),
        ("email", "Email"),
    )

    type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES)
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "About Contact Info"
        verbose_name_plural = "About Contact Info"

    def __str__(self):
        return f"{self.label} - {self.value}"


class WhyChooseUsSection(models.Model):
    subtitle = models.CharField(max_length=255, default="Why Choose Us")
    title = models.CharField(max_length=255, default="Built on Trust, Driven by Results")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Why Choose Us Section"
        verbose_name_plural = "Why Choose Us Section"

    def __str__(self):
        return self.title


class WhyChooseUsCard(models.Model):
    heading = models.CharField(max_length=255)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Why Choose Us Card"
        verbose_name_plural = "Why Choose Us Cards"

    def __str__(self):
        return self.heading


class AboutResourceSection(models.Model):
    subtitle = models.CharField(max_length=255, default="Our Resources")
    title = models.CharField(max_length=255, default="Everything You Need for a Smooth Property Journey")
    description = models.TextField(blank=True, null=True)
    side_image = models.ImageField(upload_to="aboutus/resources/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "About Resource Section"
        verbose_name_plural = "About Resource Section"

    def __str__(self):
        return self.title


class AboutResourceItem(models.Model):
    heading = models.CharField(max_length=255)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "About Resource Item"
        verbose_name_plural = "About Resource Items"

    def __str__(self):
        return self.heading


class AboutTeamIntroSection(models.Model):
    subtitle = models.CharField(max_length=255, default="Our Team")
    title = models.CharField(max_length=255, default="A Dedicated Team That Truly Cares")
    paragraph_1 = models.TextField(blank=True, null=True)
    paragraph_2 = models.TextField(blank=True, null=True)
    paragraph_3 = models.TextField(blank=True, null=True)
    paragraph_4 = models.TextField(blank=True, null=True)
    side_image = models.ImageField(upload_to="aboutus/team_intro/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "About Team Intro Section"
        verbose_name_plural = "About Team Intro Section"

    def __str__(self):
        return self.title


class AboutTeamSection(models.Model):
    subtitle = models.CharField(max_length=255, default="Team Members")
    title = models.CharField(max_length=255, default="Meet Our Experts")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "About Team Section"
        verbose_name_plural = "About Team Section"

    def __str__(self):
        return self.title


class AboutTeamMember(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    designation = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="aboutus/team_members/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "About Team Member"
        verbose_name_plural = "About Team Members"

    def __str__(self):
        return self.name


class AboutGallerySection(models.Model):
    subtitle = models.CharField(max_length=255, default="Gallery")
    title = models.CharField(max_length=255, default="Our Real Estate Showcase")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "About Gallery Section"
        verbose_name_plural = "About Gallery Section"

    def __str__(self):
        return self.title


class AboutGalleryImage(models.Model):
    ROW_CHOICES = (
        (1, "Row 1"),
        (2, "Row 2"),
        (3, "Row 3"),
    )

    image = models.ImageField(upload_to="aboutus/gallery/")
    row_number = models.PositiveIntegerField(choices=ROW_CHOICES, default=1)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["row_number", "order", "id"]
        verbose_name = "About Gallery Image"
        verbose_name_plural = "About Gallery Images"

    def __str__(self):
        return f"Gallery Row {self.row_number} - {self.id}"