from django.db import models
from django.conf import settings
from apps.reports.models import Report


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='comments')
    contenu = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment #{self.id} by {self.user}"
