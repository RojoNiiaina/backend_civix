from django.db import models
from django.conf import settings
from apps.reports.models import Report


class Assignment(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignments')
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='assignments')
    statut = models.CharField(max_length=50, default='en_attente')  # ou choices si tu veux
    date_assigne = models.DateTimeField(auto_now_add=True)
    date_echeance = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Assignment #{self.id} - {self.statut}"
