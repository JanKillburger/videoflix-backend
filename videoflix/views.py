from rest_framework.viewsets import generics
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.forms import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from .serializers import SignUpSerializer
from cryptography.fernet import Fernet
import os
from .tasks import send_activation_mail, send_reset_password_email
from django_rq import get_queue
from datetime import datetime

default_queue = get_queue("default")
#Tokens for resetting password expire after 10 minutes
TOKEN_EXPIRY_DURATION = 10 * 60 
# Create your views here.

class SignUpView(generics.CreateAPIView):
  serializer_class = SignUpSerializer
  queryset = get_user_model().objects.all()

  def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # validate password with django built-in validators (requires User instance)
        User = get_user_model()
        user_to_validate = User(**serializer.validated_data)
        try:
            validate_password(user_to_validate.password, user_to_validate)
        except ValidationError as error:
            return Response({"password": error}, status=status.HTTP_400_BAD_REQUEST)
        # create user and user token and return it
        user = get_user_model().objects.create_user(**serializer.validated_data)
        # token = Token.objects.create(user=user)
        key = os.getenv('FERNET_KEY').encode('utf-8')
        f = Fernet(key)
        activation_token = f.encrypt(user.email.encode('utf-8')).decode('utf-8')
        send_activation_mail(user.email, activation_token)
        response = {
            "message": "User account has been created. Please check your mails for activation link."
        }
        headers = self.get_success_headers(serializer.data)
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)
      
  

@api_view(['GET'])
def activate_user(request):
    if 'activationtoken' in request.query_params:
        useremail_encrypted = request.query_params['activationtoken']
        key = os.getenv('FERNET_KEY').encode('utf-8')
        f = Fernet(key)
        useremail = f.decrypt(useremail_encrypted.encode('utf-8')).decode('utf-8')
        result_set = get_user_model().objects.filter(email=useremail, is_active=False)
        if len(result_set) == 0:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        user = result_set[0]
        user.is_active = True
        user.save()
        token = Token.objects.get_or_create(user=user)
        return Response({"message": "user has been activated", "token": token.key}, status=status.HTTP_200_OK)
    return Response({"error": "Missing token"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def request_password_reset(request):
    try:
        user = get_user_model().objects.get(email=request.data['email'])
    except ObjectDoesNotExist:
        return Response(status=400)
    key = os.getenv('FERNET_KEY').encode('utf-8')
    f = Fernet(key)
    reset_token = f.encrypt_at_time(user.email.encode('utf-8'), int(datetime.now().timestamp() + TOKEN_EXPIRY_DURATION)).decode('utf-8')
    default_queue.enqueue(send_reset_password_email, user.email, reset_token)
    return Response(status=200)

@api_view(['POST'])
def reset_password(request, reset_token):
    key = os.getenv('FERNET_KEY').encode('utf-8')
    f = Fernet(key)
    expiry_timestamp = f.extract_timestamp(reset_token)
    if expiry_timestamp < int(datetime.now().timestamp()):
        return Response({"message": "Expired token. Request another password reset."}, status=400)
    else:
        user_email = f.decrypt(reset_token.encode("utf-8")).decode("utf-8")
        result = get_user_model().objects.filter(email=user_email)
        if len(result) == 1:
            user = result[0]
            token = Token.objects.get(user=user)
            token.delete()
            token = Token.objects.create(user=user)
            print(token.key)
            return Response({"token": token.key, "message": "Password successfully reset."}, status=200)
        else:
            return Response({"message": "No user with this email address."}, status=400)



# Secure media files how to: 'https://forum.djangoproject.com/t/media-exposure-vulnerability/26863'
