from django.db import models
from django.utils import timezone


class JobOpening(models.Model):
    JOB_TYPE_CHOICES = (
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("internship", "Internship"),
        ("contract", "Contract"),
        ("freelance", "Freelance"),
    )

    WORK_MODE_CHOICES = (
        ("office", "Work From Office"),
        ("hybrid", "Hybrid"),
        ("remote", "Remote"),
    )

    title = models.CharField(max_length=180)
    department = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=180, default="Navi Mumbai")
    job_type = models.CharField(max_length=30, choices=JOB_TYPE_CHOICES, default="full_time")
    work_mode = models.CharField(max_length=30, choices=WORK_MODE_CHOICES, default="office")
    experience = models.CharField(max_length=120, blank=True)
    salary_range = models.CharField(max_length=120, blank=True)

    description = models.TextField()
    responsibilities = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    preferred_skills = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    keywords = models.TextField(
        blank=True,
        help_text="Add comma separated keywords, for example: Sales, Real Estate, CRM",
    )

    is_active = models.BooleanField(default=True)
    application_deadline = models.DateField(null=True, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Job Opening"
        verbose_name_plural = "Job Openings"

    def __str__(self):
        return self.title

    @property
    def is_deadline_over(self):
        if not self.application_deadline:
            return False
        return self.application_deadline < timezone.localdate()


class JobApplication(models.Model):
    STATUS_CHOICES = (
        ("new", "New"),
        ("reviewing", "Reviewing"),
        ("shortlisted", "Shortlisted"),
        ("rejected", "Rejected"),
        ("hired", "Hired"),
    )

    job = models.ForeignKey(JobOpening, on_delete=models.CASCADE, related_name="applications")
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    experience_years = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    current_company = models.CharField(max_length=160, blank=True)
    current_ctc = models.CharField(max_length=80, blank=True)
    expected_ctc = models.CharField(max_length=80, blank=True)
    notice_period = models.CharField(max_length=80, blank=True)
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to="careers/resumes/%Y/%m/")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="new")
    source = models.CharField(max_length=120, default="Website")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"

    def __str__(self):
        return f"{self.full_name} - {self.job.title}"
