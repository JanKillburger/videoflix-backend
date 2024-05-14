from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

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
        user.save(using=self._db)
        return user

class User(AbstractUser):
    username = models.CharField(unique=False, max_length=150)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __string__(self):
        return self.email

class Video(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to="videos")