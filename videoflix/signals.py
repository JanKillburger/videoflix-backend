from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
import os
from django.conf import settings
from .tasks import convert_video, create_video_poster
from django_rq import get_queue
from config import settings

default_queue = get_queue("default")

@receiver(post_save, sender=Video)
def run_convert_video(sender, instance, created, **kwargs):
  if created and instance.file and os.path.isfile(instance.file.path):
    default_queue.enqueue(convert_video, instance.file.path, instance.id)
    default_queue.enqueue(create_video_poster, instance.file.path, instance.id)

@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
  """Delete video file when Video object is deleted."""

  media_path = settings.MEDIA_ROOT #os.path.join(settings.BASE_DIR, "media", "videos")
  for file in os.listdir(media_path):
    if file.startswith(str(instance.id) + "_" ):
      os.remove(os.path.join(media_path, file))
