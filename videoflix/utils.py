import os

def delete_user_video(path):
  if os.path.isfile(path):
    os.remove(path)