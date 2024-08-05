from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """Create and save a user with the given email and password."""

        if not email:
            raise ValueError("Users must have an email address")
        
        user = self.model(
            email=self.normalize_email(email)
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None):
        """Create and save a superuser with the given email and password."""

        user = self.create_user(
            email,
            password=password
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db)
        user.user_permissions.set(self.get_admin_permissions())
        return user
    
    def get_admin_permissions(self):
        required_permissions = [
            "Can add video",
            "Can view video",
            "Can change video",
            "Can delete video",
            "Can add user",
            "Can view user",
            "Can change user",
            "Can delete user",
            "Can add video category",
            "Can view video category",
            "Can change video category",
            "Can delete video category",
        ]
        permissions = []
        for permission in required_permissions:
            permissions.append(Permission.objects.get(name=permission))

        return permissions

class User(AbstractUser):
    username = models.CharField(unique=False, max_length=150)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    poster = models.CharField(max_length=100, default='https://picsum.photos/250/143')
    src = models.CharField(max_length=100, default='')
    file = models.FileField(upload_to="videos", blank=True)
    categories = models.ManyToManyField('VideoCategory')
    featured = models.BooleanField()

    def __str__(self):
        return self.title
    
class VideoCategory(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title