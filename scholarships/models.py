from django.db import models
from django.utils.text import slugify


# ── Taxonomy models ──

class StudyLevel(models.Model):
    """Degree level taxonomy: Undergraduate, Masters, PhD, etc."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Study Levels'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FundingType(models.Model):
    """Funding type taxonomy: Fully Funded, Partially Funded, etc."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Funding Types'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Country(models.Model):
    """Country taxonomy with flag emoji."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    flag = models.CharField(max_length=10, blank=True, help_text="Flag emoji, e.g. 🇺🇸")
    code = models.CharField(max_length=2, blank=True, help_text="ISO 3166-1 alpha-2, e.g. US")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.flag} {self.name}" if self.flag else self.name


class FieldOfStudy(models.Model):
    """Field of study taxonomy: Engineering, Computer Science, etc."""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Fields of Study'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ── Main scholarship model ──

class Scholarship(models.Model):
    """Scholarship listing model."""

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='scholarships')
    degree_level = models.ForeignKey(StudyLevel, on_delete=models.PROTECT, related_name='scholarships')
    field_of_study = models.ForeignKey(FieldOfStudy, on_delete=models.PROTECT, related_name='scholarships')
    funding_type = models.ForeignKey(FundingType, on_delete=models.PROTECT, related_name='scholarships')
    funding_amount = models.CharField(max_length=200, blank=True)
    deadline = models.DateField()
    application_url = models.URLField(max_length=500, blank=True, help_text="URL where students can apply")
    image_url = models.URLField(max_length=500, blank=True, help_text="Scholarship card image URL")
    description = models.TextField()
    eligibility_criteria = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            base_slug = self.slug
            counter = 1
            while Scholarship.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
