import os
from cryptography.fernet import Fernet

def delete_user_video(path):
  if os.path.isfile(path):
    os.remove(path)

def create_token(input):
  key = os.getenv('FERNET_KEY').encode('utf-8')
  f = Fernet(key)
  return f.encrypt(input.encode('utf-8')).decode('utf-8')