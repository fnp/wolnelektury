from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import club.models
from . import models


@receiver(post_delete, sender=models.MediaInsertText)
@receiver(post_save, sender=models.MediaInsertText)
def update_etag(sender, instance, **kwargs):
    instance.media_insert_set.update_etag()


@receiver(post_save, sender=club.models.Schedule)
def update_progress(sender, instance, **kwargs):
    try:
        models.Banner.update_all_progress()
    except:
        pass
