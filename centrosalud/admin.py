from django.contrib import admin
from .models import (
    CentroSalud,
    AreaCategory,
    Area,
    Paciente,
    FichaMedica,
    TratamientoMedico,
    AtencionMedica,
    ExamenMedico,
    AtencionExamen,
)

@admin.register(CentroSalud)
class CentroSaludAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "telefono")
    search_fields = ("nombre", "tipo")

@admin.register(AreaCategory)
class AreaCategoryAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo")
    list_filter = ("tipo",)
    search_fields = ("nombre",)

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "centro_salud", "categoria")
    list_filter = ("centro_salud", "categoria")
    search_fields = ("nombre",)

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido1", "rut")
    search_fields = ("nombre", "apellido1", "rut")

@admin.register(FichaMedica)
class FichaMedicaAdmin(admin.ModelAdmin):
    list_display = ("paciente", "estado")
    list_filter = ("estado",)
    search_fields = ("paciente__nombre", "paciente__apellido1")

@admin.register(TratamientoMedico)
class TratamientoMedicoAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)

@admin.register(AtencionMedica)
class AtencionMedicaAdmin(admin.ModelAdmin):
    list_display = ("ficha_medica", "medico_responsable", "area", "fecha_entrada", "fecha_salida")
    list_filter = ("area", "fecha_entrada")
    search_fields = ("ficha_medica__paciente__nombre", "medico_responsable__username")

@admin.register(ExamenMedico)
class ExamenMedicoAdmin(admin.ModelAdmin):
    list_display = ("nombre_examen",)
    search_fields = ("nombre_examen",)

@admin.register(AtencionExamen)
class AtencionExamenAdmin(admin.ModelAdmin):
    list_display = ("atencion_medica", "examen_medico", "fecha_solicitud", "fecha_resultado")
    list_filter = ("fecha_solicitud",)
    search_fields = ("examen_medico__nombre_examen",)
