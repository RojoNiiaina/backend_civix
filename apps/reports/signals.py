from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
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


@receiver(post_save, sender=Report)
def notify_new_report(sender, instance, created, **kwargs):
    """Notifie les agents et admins quand un nouveau report est créé"""
    if created:
        channel_layer = get_channel_layer()
        
        # Préparer les données du report
        report_data = {
            'id': instance.id,
            'description': instance.description,
            'lieu': instance.lieu,
            'statut': instance.statut,
            'created_at': instance.created_at.isoformat(),
            'user': {
                'id': instance.user.id,
                'nom': getattr(instance.user, 'nom', ''),
                'email': instance.user.email
            },
            'like': instance.like
        }
        
        # Notifier tous les agents
        async_to_sync(channel_layer.group_send)(
            'reports_agents',
            {
                'type': 'report_created',
                'report': report_data
            }
        )
        
        # Notifier tous les admins
        async_to_sync(channel_layer.group_send)(
            'reports_admin',
            {
                'type': 'report_created',
                'report': report_data
            }
        )
        
        # Notifier l'utilisateur qui a créé le report
        async_to_sync(channel_layer.group_send)(
            f'reports_user_{instance.user.id}',
            {
                'type': 'report_created',
                'report': report_data
            }
        )


@receiver(post_save, sender=Report)
def notify_report_update(sender, instance, created, **kwargs):
    """Notifie quand un report est mis à jour (changement de statut, etc.)"""
    if not created:  # Seulement pour les mises à jour, pas les créations
        channel_layer = get_channel_layer()
        
        # Préparer les données du report
        report_data = {
            'id': instance.id,
            'description': instance.description,
            'lieu': instance.lieu,
            'statut': instance.statut,
            'created_at': instance.created_at.isoformat(),
            'user': {
                'id': instance.user.id,
                'nom': getattr(instance.user, 'nom', ''),
                'email': instance.user.email
            },
            'like': instance.like
        }
        
        # Notifier tous les agents
        async_to_sync(channel_layer.group_send)(
            'reports_agents',
            {
                'type': 'report_updated',
                'report': report_data
            }
        )
        
        # Notifier tous les admins
        async_to_sync(channel_layer.group_send)(
            'reports_admin',
            {
                'type': 'report_updated',
                'report': report_data
            }
        )
        
        # Notifier l'utilisateur propriétaire du report
        async_to_sync(channel_layer.group_send)(
            f'reports_user_{instance.user.id}',
            {
                'type': 'report_updated',
                'report': report_data
            }
        )
