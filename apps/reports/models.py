from django.db import models
from django.conf import settings


class Report(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
        ('rejete', 'Rejeté'),
    ]

    id = models.BigAutoField(primary_key=True)
    like = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    description = models.TextField()
    lieu = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to='', null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report #{self.id} - {self.statut}"


class Like(models.Model):
    """Modèle pour suivre les likes des utilisateurs sur les reports"""
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'report']  # Un utilisateur ne peut liker qu'une fois un report

    def __str__(self):
        return f"{self.user.nom} liked Report #{self.report.id}"
