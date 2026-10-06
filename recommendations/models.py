from django.db import models
from django.conf import settings


class Recommendation(models.Model):
    """ML-generated scholarship recommendation for a user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    scholarship = models.ForeignKey('scholarships.Scholarship', on_delete=models.CASCADE, related_name='recommendations')
    score = models.FloatField()
    rank = models.PositiveIntegerField()
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['rank']
        unique_together = ('user', 'scholarship')

    def __str__(self):
        return f"{self.user.email} - {self.scholarship.title} ({self.score:.2f})"
