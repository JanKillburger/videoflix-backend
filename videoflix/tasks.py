from django.core.mail import send_mail
from config.settings import DEFAULT_FROM_EMAIL
from django_rq import job
import os

import logging
import subprocess

logger = logging.getLogger(__name__)


@job
def send_activation_mail(to, activation_token):
  send_mail(
              "Your Videoflix user account has been created",
              "Welcome to Videoflix!",
              "no-reply@videoflix.com",
              {to},
              html_message=f"<p>Please activate your user account by clicking on the link:</p><br><a href='http://127.0.0.1:8000/activate/?activationtoken={activation_token}'>Activate your account</a>",
              fail_silently=False
          )
  
@job
def convert_video(path, obj_id):
  dest = os.path.join(os.path.dirname(path))
  file_name = str(obj_id) + "_" + os.path.splitext(os.path.basename(path))[0] + ".m3u8"
  output_path = os.path.join(dest, file_name)
  cmd = f"ffmpeg -i {path} -codec: copy -start_number 0 -hls_time 6 -hls_list_size 0 -f hls {output_path}"
  subprocess.run(cmd, check=True, shell=True)
  delete_user_video(path)

@job
def delete_user_video(path):
  if os.path.isfile(path):
    os.remove(path)