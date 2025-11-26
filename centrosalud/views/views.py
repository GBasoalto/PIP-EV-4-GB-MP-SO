from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import redirect
from login.models.models import PerfilUsuario

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        try:
            perfil = request.user.perfil
            if perfil.tipo == 'MEDICO':
                return redirect('doctor_patient_list')
            elif perfil.tipo == 'DIRECTOR':
                return redirect('director_dashboard')
            elif perfil.tipo == 'INGRESO':
                return redirect('admission_dashboard')
        except PerfilUsuario.DoesNotExist:
            pass # Fallback to default dashboard if no profile

        return super().dispatch(request, *args, **kwargs)

    # Podemos pasar contexto opcional si queremos
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.request.user
        return context