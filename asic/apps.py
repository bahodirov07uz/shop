from django.apps import AppConfig


class AsicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'asic'

def ready(self):
    import asic.signals