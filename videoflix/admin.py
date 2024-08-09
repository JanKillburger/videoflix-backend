from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User, Video, VideoCategory
from .forms import UserCreationForm, UserAdmin, UserChangeForm
# Register your models here.

admin.site.unregister(Group)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
  add_form = UserCreationForm
  form = UserChangeForm

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
  list_display = ("title", "description", "list_categories", "featured")
  list_filter = ("categories", "featured")

  def list_categories(self, obj):
    categories = [c.title for c in obj.categories.all()]
    return ", ".join(categories)
    
  list_categories.short_description = "Categories"

admin.site.register(VideoCategory)
