from django import forms
from django.contrib.auth.models import User
from .models import Profile
from .models import DonationReceiptRequest, Address
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


class AddressUpdateForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "address_line",
            "country",
            "state",
            "district",
            "village_or_post",
            "pincode",
        ]
        widgets = {
            "address_line": forms.Textarea(attrs={"class": "textarea textarea-bordered w-full"}),
            "country": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "state": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "district": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "village_or_post": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "pincode": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
        }
      
class DonationReceiptForm(forms.ModelForm):

    donor_type = forms.ChoiceField(
        choices=DonationReceiptRequest.DONOR_TYPE_CHOICES,
        widget=forms.RadioSelect,initial="INDIAN"
        
    )

    auto_fill = forms.BooleanField(
        required=False,
        label="Use my profile details"
    )

    
    class Meta:
        model = DonationReceiptRequest
        fields = [
            "donor_type",
            "donor_name",
            "pan_number",
            "donation_amount",
            "address",
            "country",
            "state",
            "district",
            "pincode",
            "email",
            "mobile",
        ]

        widgets = {
            "donor_name": forms.TextInput(attrs={"class": "input input-bordered w-full","placeholder": "Donor / Institute Name"}),
            "pan_number": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "ABCDE1234F"
            }),
            "donation_amount": forms.NumberInput(attrs={
                "class": "input input-bordered w-full",
                "min": "1","placeholder": "Amount in INR"
            }),
            "address": forms.Textarea(attrs={"class": "textarea textarea-bordered w-full","placeholder": "Complete Address"}),
            "country": forms.TextInput(attrs={"value": "India"}),  # Pre-fill since default="India"
            "state": forms.TextInput(attrs={"class": "input input-bordered w-full","placeholder":"Enter State"}),
            "district": forms.TextInput(attrs={"class": "input input-bordered w-full","placeholder":"Enter District"}),
            "pincode": forms.TextInput(attrs={"class": "input input-bordered w-full","placeholder": "Pincode"}),
            "email": forms.EmailInput(attrs={"class": "input input-bordered w-full","placeholder": "Enter Email Id"}),
            "mobile": forms.TextInput(attrs={"class": "input input-bordered w-full","placeholder": "Enter Mobile No."}),
        }

    def clean_pan_number(self):
        pan = self.cleaned_data.get("pan_number")
        donor_type = self.cleaned_data.get("donor_type")

        if donor_type == "INDIAN" and not pan:
            raise forms.ValidationError("PAN number is mandatory for Indian donors.")

        return pan

    def clean(self):
        cleaned_data = super().clean()
        required_fields = [
            "donor_name",
            "donation_amount",
            "address",
            "country",
            "state",
            "district",
            "pincode",
            "email",
            "mobile",
        ]

        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, "This field is mandatory.")

        return cleaned_data
