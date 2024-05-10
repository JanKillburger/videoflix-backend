from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User
from .forms import UserCreationForm, UserAdmin, UserChangeForm
# Register your models here.

admin.site.unregister(Group)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
  add_form = UserCreationForm
  form = UserChangeForm
