from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Like, Report


@receiver(post_save, sender=Like)
def update_report_like_count_on_create(sender, instance, created, **kwargs):
    """Met à jour le compteur de likes quand un like est créé"""
    if created:
        instance.report.like = instance.report.likes.count()
        instance.report.save(update_fields=['like'])


@receiver(post_delete, sender=Like)
def update_report_like_count_on_delete(sender, instance, **kwargs):
    """Met à jour le compteur de likes quand un like est supprimé"""
    instance.report.like = instance.report.likes.count()
    instance.report.save(update_fields=['like'])
