from django.apps import AppConfig


class ReportsConfig(AppConfig):
    name = 'apps.reports'
    
    def ready(self):
        import apps.reports.signals  # Import des signals pour les enregistrer