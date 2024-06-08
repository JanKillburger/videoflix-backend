from django.core.mail import send_mail
from config.settings import DEFAULT_FROM_EMAIL
from django_rq import job
import os
from .utils import delete_user_video

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
  

def convert_video(path, obj_id):
  dest = os.path.join(os.path.dirname(path))
  output_path_segments = os.path.join(dest, str(obj_id) + r"_v%vdata%02d.ts")
  output_path_master = str(obj_id) + "_master.m3u8"
  output_path_stream = os.path.join(dest, str(obj_id) + "_stream_%v.m3u8")
  cmd = f'ffmpeg -i {path} \
    -filter_complex \
    "[0:v]split=3[v1][v2][v3]; \
    [v1]copy[v1out]; [v2]scale=w=1280:h=720[v2out]; [v3]scale=w=640:h=360[v3out]" \
    -map "[v1out]" -c:v:0 libx264 -x264-params "nal-hrd=cbr:force-cfr=1" -b:v:0 5M -maxrate:v:0 5M -minrate:v:0 5M -bufsize:v:0 10M -preset slow -g 48 -sc_threshold 0 -keyint_min 48 \
    -map "[v2out]" -c:v:1 libx264 -x264-params "nal-hrd=cbr:force-cfr=1" -b:v:1 3M -maxrate:v:1 3M -minrate:v:1 3M -bufsize:v:1 3M -preset slow -g 48 -sc_threshold 0 -keyint_min 48 \
    -map "[v3out]" -c:v:2 libx264 -x264-params "nal-hrd=cbr:force-cfr=1" -b:v:2 1M -maxrate:v:2 1M -minrate:v:2 1M -bufsize:v:2 1M -preset slow -g 48 -sc_threshold 0 -keyint_min 48 \
    -f hls \
    -hls_time 6 \
    -hls_playlist_type vod \
    -hls_flags independent_segments \
    -hls_segment_type mpegts \
    -hls_segment_filename {output_path_segments} \
    -master_pl_name {output_path_master} \
    -var_stream_map "v:0 v:1 v:2" {output_path_stream}'
  subprocess.run(cmd, check=True, shell=True)
  delete_user_video(path)
