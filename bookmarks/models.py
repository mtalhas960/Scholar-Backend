from django.db import models
from django.conf import settings


class Bookmark(models.Model):
    """Saved scholarship by a user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    scholarship = models.ForeignKey('scholarships.Scholarship', on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'scholarship')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} -> {self.scholarship.title}"
