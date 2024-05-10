from rest_framework.viewsets import generics
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.forms import ValidationError
from rest_framework.response import Response
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from .serializers import SignUpSerializer
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
        response = {
            "email": user.email,
            # "token": token.key
        }

        headers = self.get_success_headers(serializer.data)
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)

