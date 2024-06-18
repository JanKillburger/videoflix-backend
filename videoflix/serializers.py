from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Video

class SignUpSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = get_user_model()
    fields = ["email", "password"]
    extra_kwargs = {"password": {"write_only": True}}