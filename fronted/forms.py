from django import forms
from .models import Address

# --------------------- ✅ ADDRESS FORM (UNCHANGED) --------------------- #
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'full_name', 'phone', 'address_line', 'city',
            'state', 'postal_code', 'country', 'address_type', 'is_default'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number'
            }),
            'address_line': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your complete address (House No., Building, Street, Area)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your city'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your state'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter postal code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your country'
            }),
            'address_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and len(phone) != 10:
            raise forms.ValidationError("Phone number must be 10 digits.")
        return phone

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code and len(postal_code) != 6:
            raise forms.ValidationError("Postal code must be 6 digits.")
        return postal_code


# --------------------- ✅ CONTACT US FORM --------------------- #

class ContactForm(forms.Form):
    name = forms.CharField(
        label="Your Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your name'
        })
    )

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

    subject = forms.CharField(
        label="Subject",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter subject'
        })
    )

    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Write your message...',
            'rows': 4
        })
    )
