from django.views.generic import ListView, UpdateView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from login.models import PerfilUsuario
from login.forms import PerfilUsuarioForm

# LISTA DE USUARIOS DEL SISTEMA (admin del dashboard)
class ListaUsuariosView(ListView):
    model = User
    template_name = "usuarios/lista_usuarios.html"
    context_object_name = "usuarios"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        forms = {}
        for u in context["usuarios"]:
            perfil, _ = PerfilUsuario.objects.get_or_create(user=u)
            forms[u.id] = PerfilUsuarioForm(instance=perfil)

        context["forms"] = forms
        return context



# EDITAR PERFIL DE USUARIO
class EditarPerfilUsuarioView(UpdateView):
    model = PerfilUsuario
    form_class = PerfilUsuarioForm
    template_name = "usuarios/editar_usuario.html"
    success_url = reverse_lazy("lista_usuarios")

    def get_object(self):
        user_id = self.kwargs["pk"]
        usuario = get_object_or_404(User, pk=user_id)
        perfil, creado = PerfilUsuario.objects.get_or_create(user=usuario)
        return perfil

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usuario"] = self.object.user
        return context

    


