from django.apps import AppConfig

class FrontedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fronted'
    verbose_name = 'Admin Panel'

    def ready(self):
        import fronted.signals
