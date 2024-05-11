from rest_framework.viewsets import generics
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.forms import ValidationError
from rest_framework.response import Response
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from .serializers import SignUpSerializer
from cryptography.fernet import Fernet
import os
from django.core.mail import send_mail
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
        send_mail(
            "Your Videoflix user account has been created",
            "Welcome to Videoflix!",
            "no-reply@videoflix.com",
            [user.email],
            html_message=f"<p>Please activate your user account by clicking on the link:</p><br><a href='http://127.0.0.1:8000/activate/?activationtoken={activation_token}'>Activate your account</a>",
            fail_silently=False
        )
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

        return Response({"message": "user has been activated"}, status=status.HTTP_200_OK)
    return Response({"error": "Missing token"}, status=status.HTTP_400_BAD_REQUEST)
    