from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class CustomLoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Usuario o contraseña incorrectos. Por favor vuelva a intentar.",
        "inactive": "Esta cuenta esta inactiva. Contacta al administrador.",
    }
    
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su correo electrónico',
            'autocomplete': 'email'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if not re.match(r'^[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Por favor ingrese un correo electrónico valido.")
        
        return email
    
class PasswordResetConfirmForm(forms.Form):
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su nueva contraseña',
            'autocomplete': 'new-password'
        })
    )
    new_password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme su nueva contraseña',
            'autocomplete': 'new-password'
        })
    )
    
    def clean_new_password(self):
        password = self.cleaned_data.get('new_password1')
        
        # Validación de longitud mínima
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula")
        
        if not re.search(r'\d', password):
            raise ValidationError("La contraseña debe contener al menos un número.")
        
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data
        
        
