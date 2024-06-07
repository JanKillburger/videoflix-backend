from django.core.mail import send_mail
from config.settings import DEFAULT_FROM_EMAIL
from django_rq import job

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
def convert_video(path):
  print(path)