from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
import os
from .tasks import convert_video

@receiver(post_save, sender=Video)
def run_convert_video(sender, instance, created, **kwargs):
  if created and instance.file and os.path.isfile(instance.file.path):
    convert_video(instance.file.path, instance.id)

@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
  """Delete video file when Video object is deleted."""

  if instance.file:
    if os.path.isfile(instance.file.path):
      os.remove(instance.file.path)
