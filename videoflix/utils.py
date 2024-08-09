import os
from cryptography.fernet import Fernet

def delete_user_video(path):
  if os.path.isfile(path):
    os.remove(path)

def create_token(input, timestamp = None):
  key = os.getenv('FERNET_KEY').encode('utf-8')
  f = Fernet(key)
  if timestamp is None:
    return f.encrypt(input.encode('utf-8')).decode('utf-8')
  else:
    return f.encrypt_at_time(input.encode('utf-8'), timestamp).decode('utf-8')