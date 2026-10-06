from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model using email for authentication."""
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    profile_photo = models.URLField(max_length=500, blank=True, help_text="Profile photo URL")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return self.email


class Profile(models.Model):
    """Student academic profile linked to User."""

    DEGREE_LEVEL_CHOICES = [
        ('bachelors', 'Bachelors'),
        ('masters', 'Masters'),
        ('phd', 'PhD'),
        ('diploma', 'Diploma'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    degree_level = models.CharField(max_length=20, choices=DEGREE_LEVEL_CHOICES, blank=True)
    field_of_study = models.ManyToManyField('scholarships.FieldOfStudy', blank=True, related_name='student_profiles')
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    funding_preferences = models.ManyToManyField('scholarships.FundingType', blank=True, related_name='student_profiles')
    preferred_countries = models.ManyToManyField('scholarships.Country', blank=True, related_name='interested_students')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.email}"
