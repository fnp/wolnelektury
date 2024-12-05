from django.apps import AppConfig


class AnnoyConfig(AppConfig):
    name = 'annoy'

    def ready(self):
        from . import signals
