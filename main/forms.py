from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox




class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        # widgets = {
        #     "first_name": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
        #     "last_name": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
        #     "email": forms.EmailInput(attrs={"class": "input input-bordered w-full"}),
        # }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone", "bio", "avatar"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "bio": forms.Textarea(attrs={"class": "textarea textarea-bordered w-full"}),
        }

