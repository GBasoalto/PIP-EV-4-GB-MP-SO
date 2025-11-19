from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from login.forms import PasswordResetRequestForm, PasswordResetConfirmForm
from login.models import PasswordResetToken


@login_required
def home(request):
    user = request.user
    groups = user.groups.all()
    return render(request, 'home/index.html', {
        'title': 'Bienvenido',
        'user': user,
        'groups': groups,
    })


class PasswordResetRequestView(View):
    """Vista para solicitar recuperación de contraseña"""
    template_name = 'login/password_reset_request.html'
    
    def get(self, request):
        form = PasswordResetRequestForm()
        return render(request, self.template_name, {
            'form': form,
            'title': 'Recuperar Contraseña'
        })
    
    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            
            # Verificar que la cuenta esté activa
            if not user.is_active:
                messages.error(request, 'Esta cuenta está inactiva. Contacta al administrador.')
                return render(request, self.template_name, {
                    'form': form,
                    'title': 'Recuperar Contraseña'
                })
            
            # Crear token único
            token = PasswordResetToken.objects.create(user=user)
            
            # Generar URL de recuperación
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'token': str(token.token)})
            )
            
            # Enviar email
            subject = 'Recuperación de Contraseña - Sistema Salud Maule'
            message = f'''
Hola {user.first_name or user.username},

Has solicitado recuperar tu contraseña en el Sistema de Gestión de Pacientes.

Para restablecer tu contraseña, haz clic en el siguiente enlace:
{reset_url}

Este enlace expirará en 1 hora.

Si no solicitaste este cambio, ignora este mensaje.

---
Sistema de Salud Región del Maule
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Se ha enviado un correo con instrucciones para recuperar tu contraseña.')
            return redirect('password_reset_done')
        
        return render(request, self.template_name, {
            'form': form,
            'title': 'Recuperar Contraseña'
        })


class PasswordResetConfirmView(View):
    """Vista para confirmar y cambiar la contraseña"""
    template_name = 'login/password_reset_confirm.html'
    
    def get(self, request, token):
        # Validar token
        token_obj = get_object_or_404(PasswordResetToken, token=token)
        
        if not token_obj.is_valid():
            messages.error(request, 'El enlace ha expirado o ya fue utilizado.')
            return redirect('login')
        
        form = PasswordResetConfirmForm()
        return render(request, self.template_name, {
            'form': form,
            'token': token,
            'title': 'Restablecer Contraseña'
        })
    
    def post(self, request, token):
        token_obj = get_object_or_404(PasswordResetToken, token=token)
        
        if not token_obj.is_valid():
            messages.error(request, 'El enlace ha expirado o ya fue utilizado.')
            return redirect('login')
        
        form = PasswordResetConfirmForm(request.POST)
        
        if form.is_valid():
            # Cambiar contraseña
            user = token_obj.user
            new_password = form.cleaned_data['new_password1']
            user.set_password(new_password)
            user.save()
            
            # Marcar token como usado
            token_obj.used = True
            token_obj.save()
            
            messages.success(request, 'Tu contraseña ha sido restablecida exitosamente.')
            return redirect('password_reset_complete')
        
        return render(request, self.template_name, {
            'form': form,
            'token': token,
            'title': 'Restablecer Contraseña'
        })