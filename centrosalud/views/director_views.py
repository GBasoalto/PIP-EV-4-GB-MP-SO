from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from centrosalud.models.models import AtencionMedica

class DirectorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.perfil.tipo == 'DIRECTOR'

class DirectorDashboardView(LoginRequiredMixin, DirectorRequiredMixin, ListView):
    model = AtencionMedica
    template_name = 'centrosalud/director/dashboard.html'
    context_object_name = 'atenciones'

    def get_queryset(self):
        # Show active attentions (where patient is currently being treated)
        # Requirement: "Como director quiero saber que doctor atiende a cada paciente"
        # We can filter by active status in FichaMedica or just show latest attentions
        return AtencionMedica.objects.select_related('ficha_medica__paciente', 'medico_responsable').order_by('-fecha_entrada')
