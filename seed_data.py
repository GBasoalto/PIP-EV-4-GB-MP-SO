# -*- coding: utf-8 -*-
import os
import django
import random
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ev4.settings')
django.setup()

from django.contrib.auth.models import User
from centrosalud.models.models import CentroSalud, Area, AreaCategory, Paciente, FichaMedica, AtencionMedica
from login.models.models import PerfilUsuario

def create_seed_data():
    print("Iniciando carga de datos...")

    # 1. Crear Centros de Salud
    hospital_maule, _ = CentroSalud.objects.get_or_create(
        nombre="Hospital Regional del Maule",
        defaults={'direccion': "Calle 1 Norte 123", 'telefono': "712223344", 'tipo': "HOSPITAL"}
    )
    hospital_cauquenes, _ = CentroSalud.objects.get_or_create(
        nombre="Hospital San Juan de Dios de Cauquenes",
        defaults={'direccion': "Av. San Martín 567", 'telefono': "712334455", 'tipo': "HOSPITAL"}
    )
    cesfam, _ = CentroSalud.objects.get_or_create(
        nombre="CESFAM La Florida",
        defaults={'direccion': "Av. La Florida 456", 'telefono': "712556677", 'tipo': "CESFAM"}
    )
    print(f"[OK] Centros de salud: {hospital_maule.nombre}, {hospital_cauquenes.nombre}, {cesfam.nombre}")

    # 2. Crear Categorias de Areas
    cat_hospital, _ = AreaCategory.objects.get_or_create(
        nombre="Areas de Hospital",
        tipo="HOSPITAL"
    )
    cat_cesfam, _ = AreaCategory.objects.get_or_create(
        nombre="Areas de CESFAM",
        tipo="CESFAM"
    )
    print(f"[OK] Categorias creadas: {cat_hospital.nombre}, {cat_cesfam.nombre}")

    # 3. Crear Areas para Hospital Regional del Maule
    areas_hospital = ["UCI", "Hospitalizacion", "Urgencias", "Parto", "Laboratorio", 
                      "Banco de sangre", "Imagenologia", "Sala de espera"]
    for nombre in areas_hospital:
        area, created = Area.objects.get_or_create(
            nombre=nombre, 
            centro_salud=hospital_maule,
            defaults={'categoria': cat_hospital}
        )
        if not created and area.categoria != cat_hospital:
            area.categoria = cat_hospital
            area.save()
    print(f"[OK] Areas de Hospital Maule creadas/actualizadas: {len(areas_hospital)}")
    
    # 3b. Crear Areas para Hospital San Juan de Dios de Cauquenes
    for nombre in areas_hospital:
        area, created = Area.objects.get_or_create(
            nombre=nombre, 
            centro_salud=hospital_cauquenes,
            defaults={'categoria': cat_hospital}
        )
        if not created and area.categoria != cat_hospital:
            area.categoria = cat_hospital
            area.save()
    print(f"[OK] Areas de Hospital Cauquenes creadas/actualizadas: {len(areas_hospital)}")
    
    # 4. Crear Areas para CESFAM
    areas_cesfam = ["Banco de sangre", "Odontologia", "Sala de espera"]
    for nombre in areas_cesfam:
        area, created = Area.objects.get_or_create(
            nombre=nombre, 
            centro_salud=cesfam,
            defaults={'categoria': cat_cesfam}
        )
        if not created and area.categoria != cat_cesfam:
            area.categoria = cat_cesfam
            area.save()
    print(f"[OK] Areas de CESFAM creadas/actualizadas: {len(areas_cesfam)}")

    # 5. Crear Usuarios
    usuarios_data = [
        {"username": "manuel_medico", "first_name": "Manuel", "last_name": "Poblete", "rol": "MEDICO", "email": "manuel@cftsa.cl", "centro": hospital_maule},
        {"username": "gonzalo_director", "first_name": "Gonzalo", "last_name": "Basoalto", "rol": "DIRECTOR", "email": "gonzalo@cftsa.cl", "centro": hospital_maule},
        {"username": "alen_ingreso", "first_name": "Alen", "last_name": "Opazo", "rol": "INGRESO", "email": "alen@cftsa.cl", "centro": hospital_maule},
        {"username": "pedro_medico", "first_name": "Pedro", "last_name": "Sánchez", "rol": "MEDICO", "email": "pedro@cftsa.cl", "centro": hospital_maule},
    ]

    for data in usuarios_data:
        if not User.objects.filter(username=data["username"]).exists():
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password="12345678",
                first_name=data["first_name"],
                last_name=data["last_name"]
            )
            PerfilUsuario.objects.create(
                user=user,
                tipo=data["rol"],
                centro_salud=data["centro"],
                rut=f"{random.randint(10000000, 25000000)}-{random.randint(0, 9)}"
            )
            print(f"[OK] Usuario creado: {data['username']} ({data['rol']}) - {data['centro'].nombre}")
        else:
            user = User.objects.get(username=data["username"])
            if hasattr(user, 'perfil'):
                user.perfil.centro_salud = data["centro"]
                user.perfil.save()
                print(f"[UPD] Usuario actualizado: {data['username']} - {data['centro'].nombre}")

    # 6. Crear Pacientes con Casos Realistas
    medico = User.objects.get(username="manuel_medico")
    
    # Obtener areas del CESFAM para asignar a las atenciones
    areas_cesfam_objs = list(Area.objects.filter(centro_salud=cesfam))
    
    # PACIENTE 1: Adulto mayor con enfermedad cronica
    paciente1_rut = "15234567-8"
    if not Paciente.objects.filter(rut=paciente1_rut).exists():
        paciente1 = Paciente.objects.create(
            nombre="Roberto",
            apellido1="Silva",
            apellido2="Mendoza",
            rut=paciente1_rut,
            fecha_nacimiento=date(1955, 3, 15),  # 68 anios
            telefono="912345678",
            direccion="Av. Los Heroes 234, Talca"
        )
        ficha1 = FichaMedica.objects.create(
            paciente=paciente1,
            estado='EN_TRATAMIENTO',
            antecedentes_personales="Hipertension arterial desde hace 10 anios",
            alergias="Penicilina",
            enfermedades_cronicas="Diabetes tipo 2, Hipertension",
            medicamentos_actuales="Metformina 850mg, Enalapril 10mg"
        )
        AtencionMedica.objects.create(
            ficha_medica=ficha1,
            medico_responsable=medico,
            area=areas_cesfam_objs[0] if areas_cesfam_objs else None,
            motivo_consulta="Dolor precordial y dificultad respiratoria",
            diagnostico="Angina de pecho estable",
            tratamiento="Nitroglicerina sublingual PRN, observacion 24hrs"
        )
        print(f"[OK] Paciente 1: {paciente1.nombre} {paciente1.apellido1} (Adulto mayor con enfermedad cronica)")
    
    # PACIENTE 2: Mujer embarazada para parto
    paciente2_rut = "18765432-1"
    if not Paciente.objects.filter(rut=paciente2_rut).exists():
        paciente2 = Paciente.objects.create(
            nombre="Carolina",
            apellido1="Ramirez",
            apellido2="Torres",
            rut=paciente2_rut,
            fecha_nacimiento=date(1992, 7, 22),  # 31 anios
            telefono="923456789",
            direccion="Calle Las Rosas 456, Talca"
        )
        ficha2 = FichaMedica.objects.create(
            paciente=paciente2,
            estado='PRE_OPERATORIO',
            antecedentes_personales="Embarazo de 38 semanas, sin complicaciones previas",
            antecedentes_familiares="Madre con diabetes gestacional",
            alergias="Ninguna conocida"
        )
        AtencionMedica.objects.create(
            ficha_medica=ficha2,
            medico_responsable=medico,
            area=areas_cesfam_objs[1] if len(areas_cesfam_objs) > 1 else areas_cesfam_objs[0] if areas_cesfam_objs else None,
            motivo_consulta="Contracciones regulares cada 5 minutos",
            diagnostico="Trabajo de parto activo, embarazo a termino",
            tratamiento="Monitoreo fetal continuo, preparacion para parto vaginal"
        )
        print(f"[OK] Paciente 2: {paciente2.nombre} {paciente2.apellido1} (Embarazada en trabajo de parto)")
    
    # PACIENTE 3: Paciente post-operado
    paciente3_rut = "12987654-3"
    if not Paciente.objects.filter(rut=paciente3_rut).exists():
        paciente3 = Paciente.objects.create(
            nombre="Miguel",
            apellido1="Gonzalez",
            apellido2="Vargas",
            rut=paciente3_rut,
            fecha_nacimiento=date(1978, 11, 8),  # 45 anios
            telefono="934567890",
            direccion="Pasaje El Roble 789, Talca"
        )
        ficha3 = FichaMedica.objects.create(
            paciente=paciente3,
            estado='POST_OPERATORIO',
            antecedentes_personales="Apendicectomia hace 3 dias",
            alergias="Latex",
            medicamentos_actuales="Tramadol 50mg c/8hrs, Omeprazol 20mg c/24hrs"
        )
        AtencionMedica.objects.create(
            ficha_medica=ficha3,
            medico_responsable=medico,
            area=areas_cesfam_objs[0] if areas_cesfam_objs else None,
            motivo_consulta="Control post-operatorio",
            diagnostico="Evolucion favorable post apendicectomia, sin signos de infeccion",
            tratamiento="Continuar antibioticoterapia, alta probable en 48hrs"
        )
        print(f"[OK] Paciente 3: {paciente3.nombre} {paciente3.apellido1} (Post-operatorio en recuperacion)")
    
    # PACIENTE 4: Paciente de alta reciente
    paciente4_rut = "16543210-9"
    if not Paciente.objects.filter(rut=paciente4_rut).exists():
        paciente4 = Paciente.objects.create(
            nombre="Isabel",
            apellido1="Martinez",
            apellido2="Soto",
            rut=paciente4_rut,
            fecha_nacimiento=date(1985, 5, 30),  # 38 anios
            telefono="945678901",
            direccion="Av. San Miguel 321, Talca"
        )
        ficha4 = FichaMedica.objects.create(
            paciente=paciente4,
            estado='EN_ALTA',
            antecedentes_personales="Neumonia adquirida en comunidad tratada exitosamente",
            alergias="Ninguna conocida",
            medicamentos_actuales="Ninguno"
        )
        AtencionMedica.objects.create(
            ficha_medica=ficha4,
            medico_responsable=medico,
            area=areas_cesfam_objs[2] if len(areas_cesfam_objs) > 2 else areas_cesfam_objs[0] if areas_cesfam_objs else None,
            motivo_consulta="Control de alta post hospitalizacion por neumonia",
            diagnostico="Neumonia resuelta, paciente asintomatico",
            tratamiento="Alta medica, control ambulatorio en 7 dias"
        )
        print(f"[OK] Paciente 4: {paciente4.nombre} {paciente4.apellido1} (Alta medica reciente)")

    print("\n[COMPLETADO] Carga de datos exitosa")
    print(f"\nResumen:")
    print(f"  - Centros de salud: 2 (Hospital, CESFAM)")
    print(f"  - Categorias de areas: 2")
    print(f"  - Areas de hospital: {len(areas_hospital)}")
    print(f"  - Areas de CESFAM: {len(areas_cesfam)}")
    print(f"  - Usuarios: {len(usuarios_data)}")
    print(f"  - Pacientes: 4 (casos clinicos variados)")

if __name__ == '__main__':
    create_seed_data()
