from django import forms
from .models import CustomUser

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