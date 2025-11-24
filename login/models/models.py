from django.db import models
from django.contrib.auth.models import User
from centrosalud.models import CentroSalud
from django.utils import timezone
import uuid
from datetime import timedelta

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Token de Recuperación"
        verbose_name_plural = "Tokens de Recuperación"
        
        
    
    def is_valid(self):
        """Verifica si el token es válido (menos de 1 hora y no usado)"""
        expiration_time = self.created_at + timedelta(hours=1)
        return not self.used and timezone.now() < expiration_time
    
    def __str__(self):
        return f"Token para {self.user.username} - {'Usado' if self.used else 'Activo'}"
    

#modelos para agregar tipo a los usuarios de auth    
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    tipo = models.CharField(max_length=20) #ADMIN, MEDICO, ENFERMERA, RECEPCIONISTA
    rut = models.CharField(max_length=12, unique=True, null=True, blank=True)
    #PARA DESTINARLO A UN CENTRO DE SALUD ESPECIFICO
    centro_salud = models.ForeignKey(CentroSalud, on_delete=models.SET_NULL, null=True, blank=True) 
    foto = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.tipo})"

 





