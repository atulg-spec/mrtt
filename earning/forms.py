from django import forms
from .models import WithdrawalRequest, UserBankAccount, UserUPIAccount

class WithdrawalForm(forms.ModelForm):
    method = forms.ChoiceField(
        choices=WithdrawalRequest.METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'sr-only peer'})
    )
    
    class Meta:
        model = WithdrawalRequest
        fields = ['amount', 'method', 'bank_account', 'upi_account', 'paytm_mobile']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'pl-8 py-3 px-4 block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': '0.00',
                'min': '100',
                'step': 'any'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter bank accounts for current user
        if self.user:
            self.fields['bank_account'].queryset = UserBankAccount.objects.filter(user=self.user)
            self.fields['upi_account'].queryset = UserUPIAccount.objects.filter(user=self.user)
        
        # Set required fields based on method
        self.fields['bank_account'].required = False
        self.fields['upi_account'].required = False
        self.fields['paytm_mobile'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('method')
        amount = cleaned_data.get('amount')
        
        # Validate amount
        if amount and amount < 100:
            raise forms.ValidationError("Minimum withdrawal amount is ₹100.")
        
        # Validate method-specific fields
        if method == 'bank' and not cleaned_data.get('bank_account'):
            raise forms.ValidationError("Please select a bank account.")
        
        if method == 'upi' and not cleaned_data.get('upi_account'):
            raise forms.ValidationError("Please select a UPI account.")
        
        if method == 'paytm' and not cleaned_data.get('paytm_mobile'):
            raise forms.ValidationError("Please enter your PayTM mobile number.")
        
        # Check if user has sufficient balance
        if amount and self.user and amount > self.user.wallet.balance:
            raise forms.ValidationError("Insufficient balance for this withdrawal.")
        
        return cleaned_data


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = UserBankAccount
        fields = ['account_holder_name', 'account_number', 'ifsc_code', 'bank_name', 'branch_name']
        widgets = {
            'account_holder_name': forms.TextInput(attrs={
                'class': 'py-2 px-3 block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': 'John Doe'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'py-2 px-3 block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': '1234567890'
            }),
            'ifsc_code': forms.TextInput(attrs={
                'class': 'py-2 px-3 block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': 'ABCD0123456'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'py-2 px-3 block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': 'Bank Name'
            }),
            'branch_name': forms.TextInput(attrs={
                'class': 'py-2 px-3 block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': 'Branch Name (Optional)'
            }),
        }


class UPIAccountForm(forms.ModelForm):
    class Meta:
        model = UserUPIAccount
        fields = ['upi_id']
        widgets = {
            'upi_id': forms.TextInput(attrs={
                'class': 'py-2 px-3 block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': 'yourname@upi'
            }),
        }