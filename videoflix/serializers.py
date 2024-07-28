from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Video, VideoCategory

class SignUpSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = get_user_model()
    fields = ["email", "password"]
    extra_kwargs = {"password": {"write_only": True}}

class VideoCategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = VideoCategory
    fields = ["title"]

class VideoSerializer(serializers.ModelSerializer):
  categories = VideoCategorySerializer(many=True)
  class Meta:
    model = Video
    fields = ["id", "title", "description", "categories", "src", "poster", "featured"]