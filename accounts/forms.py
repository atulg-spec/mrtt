from django import forms
from .models import CustomUser, SelfieWithTree
from django.core.exceptions import ValidationError

class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'first_name', 'last_name']
        widgets = {
            'phone_number': forms.NumberInput(attrs={'placeholder': 'Enter your phone number'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter your last name'}),
        }


class KYCVerificationForm(forms.Form):
    aadhaar_number = forms.CharField(label='Aadhaar Number', max_length=12)
    date_of_birth = forms.DateField(
        label='Date of Birth',
        widget=forms.DateInput(attrs={'type': 'date'})  # provides date picker
    )
    pan_number = forms.CharField(label='PAN Number', max_length=10, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # current user passed from view
        super().__init__(*args, **kwargs)

    def clean_aadhaar_number(self):
        aadhaar = self.cleaned_data.get('aadhaar_number')
        if aadhaar:
            qs = CustomUser.objects.filter(aadhaar_number=aadhaar)
            if self.user and self.user.pk:  # check only if user is available
                qs = qs.exclude(pk=self.user.pk)
            if qs.exists():
                raise ValidationError("This Aadhaar number is already registered with another account.")
        return aadhaar
    
    def clean_pan_number(self):
        pan = self.cleaned_data.get('pan_number')
        if pan:
            qs = CustomUser.objects.filter(pan_number=pan)
            if self.user and self.user.pk:
                qs = qs.exclude(pk=self.user.pk)
            if qs.exists():
                raise ValidationError("This PAN number is already registered with another account.")
        return pan


class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'phone_number', 'address_line_1', 'address_line_2', 'city', 'state', 'zip_code', 'country')


class UserProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'username', 'email', 'phone_number',
            'date_of_birth', 'address_line_1', 'address_line_2',
            'city', 'state', 'country', 'zip_code',
            'aadhaar_number', 'pan_number', 'profile_picture'
        ]




class SelfieUploadForm(forms.ModelForm):
    class Meta:
        model = SelfieWithTree
        fields = ["selfie_image"]

    def clean(self):
        cleaned_data = super().clean()
        user = self.initial.get("user")

        if user and hasattr(user, "tree_selfie"):
            selfie = user.tree_selfie
            if selfie.status == "verified":
                raise forms.ValidationError("You cannot upload a new selfie after verification.")
            elif selfie.status == "pending":
                raise forms.ValidationError("Your selfie is still under review.")
        return cleaned_data
