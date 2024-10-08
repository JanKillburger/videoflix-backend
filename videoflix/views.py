from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import generics
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from django.forms import ValidationError
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from .serializers import SignUpSerializer, VideoSerializer, VideoCategorySerializer
from cryptography.fernet import Fernet
import os
from .tasks import send_activation_mail, send_reset_password_email
from django_rq import get_queue
from datetime import datetime
from .models import Video, VideoCategory
from .utils import create_token

default_queue = get_queue("default")
#Tokens for resetting password expire after 10 minutes
TOKEN_EXPIRY_DURATION = 10 * 60 
# Create your views here.

class SignUpView(generics.CreateAPIView):
  serializer_class = SignUpSerializer
  queryset = get_user_model().objects.all()
  authentication_classes = []
  permission_classes = []

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
        # create user
        user = get_user_model().objects.create_user(**serializer.validated_data)
        activation_token = create_token(user.email)
        default_queue.enqueue(send_activation_mail, user.email, activation_token)
        response = {
            "message": "User account has been created. Please check your mails for activation link."
        }
        headers = self.get_success_headers(serializer.data)
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)
      
  

@api_view(['PUT'])
@permission_classes([])
@authentication_classes([])
def activate_user(request):
    if 'activationtoken' in request.data:
        useremail_encrypted = request.data['activationtoken']
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

@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def login(request):
    if request.data['email'] is None:
        return Response({"email": ["This field may not be blank"]}, status=400)
    if request.data['password'] is None:
        return Response({"password": ["This field may not be blank"]}, status=400)
    try:
        user = get_user_model().objects.get(email=request.data['email'])
    except ObjectDoesNotExist:
        return Response({"errors": ["Wrong username and/or password"]}, status=400)
    if not user.is_active or not user.check_password(request.data['password']):
        return Response({"errors": ["Wrong username and/or password"]}, status=400)
    token, created = Token.objects.get_or_create(user=user)
    return Response({"token": token.key}, status=200)
    
@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def check_email(request):
    if request.data['email'] and get_user_model().objects.filter(email=request.data['email'], is_active=True).exists():
        return Response({"data": "Valid email"}, status=200)
    else:
        return Response({"error": ["Invalid email",]}, status=400)


@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def request_password_reset(request):
    try:
        user = get_user_model().objects.get(email=request.data['email'], is_active=True)
    except ObjectDoesNotExist:
        return Response(status=400)
    reset_token = create_token(user.email, int(datetime.now().timestamp() + TOKEN_EXPIRY_DURATION))
    default_queue.enqueue(send_reset_password_email, user.email, reset_token)
    return Response(status=200)

@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def reset_password(request, reset_token):
    key = os.getenv('FERNET_KEY').encode('utf-8')
    f = Fernet(key)
    expiry_timestamp = f.extract_timestamp(reset_token)
    if expiry_timestamp < int(datetime.now().timestamp()):
        return Response({"general": ["Expired token. Request another password reset.",]}, status=400)
    user_email = f.decrypt(reset_token.encode("utf-8")).decode("utf-8")
    result = get_user_model().objects.filter(email=user_email)
    # validate password with django built-in validators (requires User instance)
    User = get_user_model()
    user_to_validate = User(email=user_email, password=request.data['password'])
    try:
        validate_password(user_to_validate.password, user_to_validate)
    except ValidationError as error:
        return Response({"password": error}, status=status.HTTP_400_BAD_REQUEST)
    if len(result) == 1:
        user = result[0]
        token, created = Token.objects.get_or_create(user=user)
        if not created:
            token.delete()
            token = Token.objects.create(user=user)
        user.set_password(request.data['password'])
        user.save()
        return Response({"token": token.key}, status=200)
    else:
        return Response({"general": ["No user with this email address.",]}, status=400)

@api_view(['GET'])
@permission_classes([])
@authentication_classes([])
def get_media(request, **kwargs):
    response = HttpResponse()
    del response['Content-Type']
    response['X-Accel-Redirect'] = '/protected' + request.path
    return response


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    

class Videos(generics.ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def list(self, request):
        queryset = self.get_queryset()
        serializer = VideoSerializer(queryset, many=True)
        return Response(serializer.data)
    
class VideoCategories(generics.ListAPIView):
    queryset = VideoCategory.objects.filter(video__isnull=False).distinct()
    serializer_class = VideoCategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def list(self, request):
        queryset = self.get_queryset()
        serializer = VideoCategorySerializer(queryset, many=True)
        return Response(serializer.data)
# Secure media files how to: 'https://forum.djangoproject.com/t/media-exposure-vulnerability/26863'

