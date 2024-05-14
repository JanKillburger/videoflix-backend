from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_delete
import os

@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
  """Delete video file when Video object is deleted."""

  if instance.file:
    if os.path.isfile(instance.file.path):
      os.remove(instance.file.path)
