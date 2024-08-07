from django.core.mail import send_mail
from config.settings import DEFAULT_FROM_EMAIL
import os
from .utils import delete_user_video
import subprocess
from dotenv import load_dotenv
from .models import Video
from config import settings
from pathlib import Path

load_dotenv()

def send_activation_mail(to, activation_token):
  send_mail(
              "Your Videoflix user account has been created",
              f"Welcome to Videoflix! Follow this link to verify your email address: {os.getenv('FRONTEND_BASE_URL')}/login/{activation_token}",
              None,
              {to},
              html_message=f"<p>Dear {to.split('@')[0]},</p>\
                <p>thank you for registering with <span style='color:hsl(235, 73%, 53%);'>Videoflix</span>. To complete your registration and verify your email address, please click the link below:</p>\
                <p><a style='background-color: hsl(235, 73%, 53%); color: white;text-decoration:none;padding: 0.5em 1.5em;border-radius:3em;'\
                    href='{os.getenv('FRONTEND_BASE_URL')}/login/{activation_token}'>Activate account</a></p>\
                <p>If you did not create an account with us, please disregard this email.</p>\
                <p>Best regards,</p>\
                <p>Your Videoflix Team</p>",
              fail_silently=False
          )

def send_reset_password_email(email, reset_token):
  send_mail(
    "Reset your password",
    f"To reset your password, follow this link: {os.getenv('FRONTEND_BASE_URL')}/reset-password/{reset_token}",
    None,
    {email},
    html_message=f"<p>Dear {email.split('@')[0]},</p>\
      <p>We recently received a request to reset your password. If you made this request, please click on the following link to reset your password:</p>\
      <p><a style='background-color: hsl(235, 73%, 53%); color: white;text-decoration:none;padding: 0.5em 1.5em;border-radius:3em;'\
                    href='{os.getenv('FRONTEND_BASE_URL')}/reset-password/{reset_token}'>Reset password</a></p>\
      <p>Please note that for security reasons, this link is only valid for 24 hours.</p>\
      <p>If you did not request a password reset, please ignore this email.</p>\
      <p>Best regards,</p>\
      <p>Your Videoflix Team</p>"
  )

def convert_video(path, obj_id):
  dest = os.path.join(os.path.dirname(path))
  output_path_segments = os.path.join(dest, str(obj_id) + "_v%v_data%02d.ts")
  output_path_master = str(obj_id) + "_master.m3u8"
  output_path_stream = os.path.join(dest, str(obj_id) + r"_stream_%v.m3u8")
  cmd = f'ffprobe -i {path} -show_streams -select_streams a -loglevel error'
  has_audio = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout != ''
  if has_audio:
    cmd = f'\
      ffmpeg -i {path} \
        -filter_complex \
        "[0:v]split=3[v1][v2][v3]; \
        [v1]copy[v1out]; [v2]scale=w=1280:h=720[v2out]; [v3]scale=w=640:h=360[v3out]" \
        -map "[v1out]" -c:v:0 libx264 -x264-params "nal-hrd=cbr:force-cfr=1" -b:v:0 5M -maxrate:v:0 5M -minrate:v:0 5M -bufsize:v:0 10M -preset slow -g 48 -sc_threshold 0 -keyint_min 48 \
        -map "[v2out]" -c:v:1 libx264 -x264-params "nal-hrd=cbr:force-cfr=1" -b:v:1 3M -maxrate:v:1 3M -minrate:v:1 3M -bufsize:v:1 3M -preset slow -g 48 -sc_threshold 0 -keyint_min 48 \
        -map "[v3out]" -c:v:2 libx264 -x264-params "nal-hrd=cbr:force-cfr=1" -b:v:2 1M -maxrate:v:2 1M -minrate:v:2 1M -bufsize:v:2 1M -preset slow -g 48 -sc_threshold 0 -keyint_min 48 \
        -map a:0? -c:a:0 aac -b:a:0 96k -ac 2 \
        -map a:0? -c:a:1 aac -b:a:1 96k -ac 2 \
        -map a:0? -c:a:2 aac -b:a:2 48k -ac 2 \
        -f hls \
        -hls_time 2 \
        -hls_playlist_type vod \
        -hls_flags independent_segments \
        -hls_segment_type mpegts \
        -hls_segment_filename {output_path_segments} \
        -master_pl_name {output_path_master} \
        -var_stream_map "v:0,a:0 v:1,a:1 v:2,a:2" {output_path_stream} \
    '
  else:
    cmd = f'\
      ffmpeg -i {path} \
        -filter_complex \
        "[0:v]split=3[v1][v2][v3]; \
        [v1]copy[v1out]; [v2]scale=w=1280:h=720[v2out]; [v3]scale=w=640:h=360[v3out]" \
        -map "[v1out]" -c:v:0 libx264 -x264-params "nal-hrd=cbr:force-cfr=1" -b:v:0 5M -maxrate:v:0 5M -minrate:v:0 5M -bufsize:v:0 10M -preset slow -g 48 -sc_threshold 0 -keyint_min 48 \
        -map "[v2out]" -c:v:1 libx264 -x264-params "nal-hrd=cbr:force-cfr=1" -b:v:1 3M -maxrate:v:1 3M -minrate:v:1 3M -bufsize:v:1 3M -preset slow -g 48 -sc_threshold 0 -keyint_min 48 \
        -map "[v3out]" -c:v:2 libx264 -x264-params "nal-hrd=cbr:force-cfr=1" -b:v:2 1M -maxrate:v:2 1M -minrate:v:2 1M -bufsize:v:2 1M -preset slow -g 48 -sc_threshold 0 -keyint_min 48 \
        -f hls \
        -hls_time 2 \
        -hls_playlist_type vod \
        -hls_flags independent_segments \
        -hls_segment_type mpegts \
        -hls_segment_filename {output_path_segments} \
        -master_pl_name {output_path_master} \
        -var_stream_map "v:0 v:1 v:2" {output_path_stream} \
    '
  subprocess.run(cmd, check=True, shell=True)
  video = Video.objects.get(pk=obj_id)
  video.src = output_path_master
  video.save()
  #-delete_user_video(path)

def create_video_poster(path, obj_id):
  poster_name = str(obj_id) + '.jpg'
  poster_path = os.path.join(settings.MEDIA_ROOT, "posters", poster_name)
  Path(os.path.dirname(poster_path)).mkdir(parents=True, exist_ok=True)
  subprocess.run(f'ffmpeg -ss 00:00:00 -i {path} -frames:v 1 -update 1 {poster_path}', check=True, shell=True)
  video = Video.objects.get(pk=obj_id)
  video.poster = poster_name
  video.save()
