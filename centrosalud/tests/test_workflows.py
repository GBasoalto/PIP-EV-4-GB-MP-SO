from django.test import TestCase, Client
from django.contrib.auth.models import User
from centrosalud.models.models import CentroSalud, Area, Paciente, FichaMedica, AtencionMedica
from login.models.models import PerfilUsuario
from django.urls import reverse

class WorkflowTests(TestCase):
    def setUp(self):
        # Setup Institutions
        self.hospital = CentroSalud.objects.create(nombre="Hospital Regional", tipo="HOSPITAL")
        self.area_urgencia = Area.objects.create(nombre="Urgencias", centro_salud=self.hospital)
        
        # Setup Users
        self.doctor_user = User.objects.create_user(username='doctor', password='password')
        PerfilUsuario.objects.create(user=self.doctor_user, tipo='MEDICO', centro_salud=self.hospital)
        
        self.director_user = User.objects.create_user(username='director', password='password')
        PerfilUsuario.objects.create(user=self.director_user, tipo='DIRECTOR', centro_salud=self.hospital)
        
        self.admission_user = User.objects.create_user(username='admission', password='password')
        PerfilUsuario.objects.create(user=self.admission_user, tipo='INGRESO', centro_salud=self.hospital)

        self.client = Client()

    def test_admission_workflow(self):
        self.client.login(username='admission', password='password')
        
        # 1. Create Patient
        response = self.client.post(reverse('create_patient'), {
            'nombre': 'Juan',
            'apellido1': 'Perez',
            'rut': '12345678-9',
            'fecha_nacimiento': '1990-01-01',
            'telefono': '12345678',
            'direccion': 'Calle Falsa 123'
        })
        self.assertEqual(response.status_code, 302) # Redirects on success
        self.assertTrue(Paciente.objects.filter(rut='12345678-9').exists())
        paciente = Paciente.objects.get(rut='12345678-9')
        self.assertTrue(hasattr(paciente, 'ficha_medica'))

        # 2. Register Admission
        response = self.client.post(reverse('create_admission'), {
            'ficha_medica': paciente.ficha_medica.id,
            'area': self.area_urgencia.id,
            'motivo_consulta': 'Dolor de cabeza',
            'medico_responsable': self.doctor_user.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AtencionMedica.objects.filter(ficha_medica=paciente.ficha_medica).exists())
        paciente.ficha_medica.refresh_from_db()
        self.assertEqual(paciente.ficha_medica.estado, 'EN_TRATAMIENTO')

    def test_doctor_workflow(self):
        # Setup patient and admission
        paciente = Paciente.objects.create(nombre='Ana', apellido1='Gomez', rut='98765432-1', fecha_nacimiento='1985-05-05', telefono='111', direccion='Avenida 1')
        ficha = FichaMedica.objects.create(paciente=paciente)
        
        self.client.login(username='doctor', password='password')
        
        # 1. View Patient List
        response = self.client.get(reverse('doctor_patient_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana Gomez')

        # 2. View Patient Detail
        response = self.client.get(reverse('patient_detail', kwargs={'pk': paciente.pk}))
        self.assertEqual(response.status_code, 200)

        # 3. Create Atencion
        response = self.client.post(reverse('create_atencion', kwargs={'pk': paciente.pk}), {
            'motivo_consulta': 'Control',
            'diagnostico': 'Todo bien',
            'area': self.area_urgencia.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AtencionMedica.objects.count(), 1)

        # 4. Update Status
        response = self.client.post(reverse('update_patient_status', kwargs={'pk': paciente.pk}), {
            'estado': 'EN_ALTA'
        })
        self.assertEqual(response.status_code, 302)
        ficha.refresh_from_db()
        self.assertEqual(ficha.estado, 'EN_ALTA')

    def test_dashboard_redirection(self):
        # 1. Doctor Redirection
        self.client.login(username='doctor', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('doctor_patient_list'))
        self.client.logout()

        # 2. Director Redirection
        self.client.login(username='director', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('director_dashboard'))
        self.client.logout()

        # 3. Admission Redirection
        self.client.login(username='admission', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('admission_dashboard'))
        self.client.logout()

    def test_director_workflow(self):
        # Setup patient and admission
        paciente = Paciente.objects.create(nombre='Luis', apellido1='Diaz', rut='11223344-5', fecha_nacimiento='2000-01-01', telefono='222', direccion='Calle 2')
        ficha = FichaMedica.objects.create(paciente=paciente)
        AtencionMedica.objects.create(ficha_medica=ficha, medico_responsable=self.doctor_user, area=self.area_urgencia)

        self.client.login(username='director', password='password')
        
        # 1. View Dashboard
        response = self.client.get(reverse('director_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Luis Diaz')
        self.assertContains(response, 'doctor')
