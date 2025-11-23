from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


#centro de salud (Hospital, Cefam, etc)
class CentroSalud(models.Model):
    nombre = models.CharField(max_length=100) #HOSPITAL REGIONAL DEL MAULE
    direccion = models.CharField(max_length=200) 
    telefono = models.CharField(max_length=20)
    tipo = models.CharField(max_length=100)  #CEFAM, HOSPIRAL, ETC

    def __str__(self):
        return self.nombre
    
#areas dentro del centro de salud
class Area(models.Model):
    nombre = models.CharField(max_length=100) #UCI, URGENCIA, ETC
    centro_salud = models.ForeignKey(CentroSalud, on_delete=models.CASCADE)
    def __str__(self):
        return self.nombre
    
class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido1 = models.CharField(max_length=100)
    apellido2 = models.CharField(max_length=100, null=True, blank=True)
    rut = models.CharField(max_length=12, unique=True)  
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()

    def __str__(self):
        return f"{self.nombre} {self.apellido1}"

class FichaMedica(models.Model):
    #para que sea solo 1 ficha medica por paciente, y sea visible de cualquier centro hospitalario
    paciente = models.OneToOneField(Paciente,on_delete=models.CASCADE,related_name="ficha_medica")
    #paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    antecedentes_personales = models.TextField(null=True, blank=True)
    antecedentes_familiares = models.TextField(null=True, blank=True)
    alergias = models.TextField(null=True, blank=True)
    enfermedades_cronicas = models.TextField(null=True, blank=True)
    medicamentos_actuales = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"Ficha Medica de {self.paciente.nombre} {self.paciente.apellido1}"


class TratamientoMedico(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class AtencionMedica(models.Model):
    ficha_medica = models.ForeignKey(FichaMedica, on_delete=models.CASCADE, related_name="atenciones")
    medico_responsable = models.ForeignKey(User, on_delete=models.CASCADE)

    fecha_entrada = models.DateTimeField(default=timezone.now)
    fecha_salida = models.DateTimeField(null=True, blank=True)
    motivo_consulta = models.TextField(null=True, blank=True)
    diagnostico = models.TextField(null=True, blank=True)
    tratamiento = models.ForeignKey(TratamientoMedico, on_delete=models.CASCADE,
                                     null=True, blank=True)
    

    def __str__(self):
        return f"Atencion Medica de {self.ficha_medica.paciente.nombre} por {self.medico_responsable.username}"

class ExamenMedico(models.Model):    
    nombre_examen = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    requisitos = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre_examen}"
    

class AtencionExamen(models.Model):
    atencion_medica = models.ForeignKey(AtencionMedica, on_delete=models.CASCADE)
    examen_medico = models.ForeignKey(ExamenMedico, on_delete=models.CASCADE)

    fecha_solicitud = models.DateTimeField(default=timezone.now)
    fecha_resultado = models.DateTimeField(null=True, blank=True)
    resultados = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Atencion Examen {self.examen_medico.nombre_examen} para {self.atencion_medica.ficha_medica.paciente.nombre}"