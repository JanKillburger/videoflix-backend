
from django import forms
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class UserCreationForm(forms.ModelForm):
  password = forms.CharField(label="Password", widget=forms.PasswordInput)

  class Meta:
    model = User
    fields = ["email"]

  def save(self, commit=True):
    user = super().save(commit=False)
    user.set_password(self.cleaned_data["password"])
    if commit:
      user.save()
    return user
  
class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ["email", "password", "is_active", "is_admin"]
  
class UserAdmin(BaseUserAdmin):
  # The forms to add and change user instances
  form = UserChangeForm
  add_form = UserCreationForm

  # The fields to be used in displaying the User model.
  # These override the definitions on the base UserAdmin
  # that reference specific fields on auth.User.
  list_display = ["email", "is_active", "is_admin"]
  list_filter = ["is_admin"]
  fieldsets = [
      (None, {"fields": ["email", "password", "is_active"]}),
      ("Personal info", {"fields": ["first_name", "last_name"]}),
      ("Permissions", {"fields": ["is_admin"]}),
  ]
  # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
  # overrides get_fieldsets to use this attribute when creating a user.
  add_fieldsets = [
      (
          None,
          {
              "classes": ["wide"],
              "fields": ["email", "password", "is_active"],
          },
      ),
  ]
  search_fields = ["email"]
  ordering = ["email"]
  filter_horizontal = []