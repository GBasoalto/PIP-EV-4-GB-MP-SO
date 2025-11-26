from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from centrosalud.models.models import Paciente, FichaMedica, AtencionMedica, Area
from login.models.models import PerfilUsuario

class DoctorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.perfil.tipo == 'MEDICO'

class DoctorPatientListView(LoginRequiredMixin, DoctorRequiredMixin, ListView):
    model = Paciente
    template_name = 'centrosalud/doctor/patient_list.html'
    context_object_name = 'pacientes'

    def get_queryset(self):
        # Filter patients by the doctor's hospital/center if needed
        # For now, showing all patients as per requirement "Como doctor quiero ver todos los pacientes del hospital"
        # Assuming the doctor sees patients in their assigned center
        user_profile = self.request.user.perfil
        if user_profile.centro_salud:
             # Logic to filter by center could be added here if Paciente had a direct link to CentroSalud
             # or via FichaMedica -> AtencionMedica -> Area -> CentroSalud
             pass
        return Paciente.objects.all()

class PatientDetailView(LoginRequiredMixin, DoctorRequiredMixin, DetailView):
    model = Paciente
    template_name = 'centrosalud/doctor/patient_detail.html'
    context_object_name = 'paciente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ficha'] = self.object.ficha_medica
        context['atenciones'] = self.object.ficha_medica.atenciones.all().order_by('-fecha_entrada')
        return context

class UpdateAtencionMedicaView(LoginRequiredMixin, DoctorRequiredMixin, UpdateView):
    model = AtencionMedica
    fields = ['diagnostico', 'tratamiento', 'area']
    template_name = 'centrosalud/doctor/update_atencion.html'

    def get_success_url(self):
        # Redirigir al detalle del paciente
        return reverse_lazy('patient_detail', kwargs={'pk': self.object.ficha_medica.paciente.pk})


class UpdatePatientStatusView(LoginRequiredMixin, DoctorRequiredMixin, UpdateView):
    model = FichaMedica
    fields = ['estado']
    template_name = 'centrosalud/doctor/update_status.html'
    
    def get_object(self):
        paciente = get_object_or_404(Paciente, pk=self.kwargs['pk'])
        return paciente.ficha_medica

    def get_success_url(self):
        return reverse_lazy('patient_detail', kwargs={'pk': self.kwargs['pk']})
