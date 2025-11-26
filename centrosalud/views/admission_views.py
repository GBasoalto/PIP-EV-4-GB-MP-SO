from django.views.generic import CreateView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from centrosalud.models.models import Paciente, FichaMedica, AtencionMedica, Area
from django.contrib.auth.models import User
from django import forms

class AdmissionRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.perfil.tipo == 'INGRESO'

class AdmissionDashboardView(LoginRequiredMixin, AdmissionRequiredMixin, TemplateView):
    template_name = 'centrosalud/admission/dashboard.html'

class PatientSearchForm(forms.Form):
    rut = forms.CharField(max_length=12, label="RUT del Paciente", help_text="Ej: 12345678-9")

class PatientAdmissionForm(forms.ModelForm):
    area = forms.ModelChoiceField(queryset=Area.objects.none(), label="Área de Ingreso")
    medico_responsable = forms.ModelChoiceField(queryset=User.objects.filter(perfil__tipo='MEDICO'), label="Médico Responsable")
    motivo_consulta = forms.CharField(widget=forms.Textarea, label="Motivo de Consulta")
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and hasattr(user, 'perfil') and user.perfil.centro_salud:
            # Filtrar áreas según el tipo de centro del usuario
            tipo_centro = user.perfil.centro_salud.tipo
            self.fields['area'].queryset = Area.objects.filter(categoria__tipo=tipo_centro)
        else:
            # Si no tiene centro asignado, mostrar todas
            self.fields['area'].queryset = Area.objects.all()
    
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'telefono', 'direccion']

class SearchOrCreatePatientView(LoginRequiredMixin, AdmissionRequiredMixin, FormView):
    template_name = 'centrosalud/admission/search_patient.html'
    form_class = PatientSearchForm
    
    def form_valid(self, form):
        rut = form.cleaned_data['rut']
        try:
            paciente = Paciente.objects.get(rut=rut)
            
            # Verificar si el paciente tiene una ficha médica
            if hasattr(paciente, 'ficha_medica'):
                estado_actual = paciente.ficha_medica.estado
                
                # Solo permitir nuevo ingreso si el paciente está en alta
                if estado_actual != 'EN_ALTA':
                    estado_display = dict(FichaMedica.ESTADOS_PACIENTE)[estado_actual]
                    messages.error(
                        self.request,
                        f'No se puede registrar un nuevo ingreso. El paciente {paciente.nombre} {paciente.apellido1} '
                        f'tiene un registro activo en estado: {estado_display}. '
                        f'Debe estar en "En Alta" para permitir un nuevo ingreso.'
                    )
                    return redirect('search_patient')
            
            # Paciente existe y está en alta (o no tiene ficha), redirigir a registrar ingreso
            return redirect('register_admission', pk=paciente.pk)
        except Paciente.DoesNotExist:
            # Paciente no existe, redirigir a crear paciente
            return redirect('create_patient_with_rut', rut=rut)

class CreatePatientWithAdmissionView(LoginRequiredMixin, AdmissionRequiredMixin, FormView):
    template_name = 'centrosalud/admission/create_patient_admission.html'
    form_class = PatientAdmissionForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pasar el usuario al formulario
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        rut = self.kwargs.get('rut')
        if rut:
            initial['rut'] = rut
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rut'] = self.kwargs.get('rut', '')
        return context
    
    def form_valid(self, form):
        rut = self.kwargs.get('rut')
        # Crear paciente
        paciente = Paciente.objects.create(
            nombre=form.cleaned_data['nombre'],
            apellido1=form.cleaned_data['apellido1'],
            apellido2=form.cleaned_data.get('apellido2', ''),
            rut=rut,
            fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
            telefono=form.cleaned_data['telefono'],
            direccion=form.cleaned_data['direccion']
        )
        
        # Crear ficha médica
        ficha = FichaMedica.objects.create(paciente=paciente, estado='EN_TRATAMIENTO')
        
        # Crear atención médica
        AtencionMedica.objects.create(
            ficha_medica=ficha,
            medico_responsable=form.cleaned_data['medico_responsable'],
            area=form.cleaned_data['area'],
            motivo_consulta=form.cleaned_data['motivo_consulta']
        )
        
        messages.success(self.request, f'Paciente {paciente.nombre} {paciente.apellido1} ingresado exitosamente.')
        return redirect('admission_dashboard')

class RegisterAdmissionView(LoginRequiredMixin, AdmissionRequiredMixin, CreateView):
    model = AtencionMedica
    fields = ['area', 'motivo_consulta', 'medico_responsable']
    template_name = 'centrosalud/admission/register_admission.html'
    success_url = reverse_lazy('admission_dashboard')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar solo médicos
        form.fields['medico_responsable'].queryset = User.objects.filter(perfil__tipo='MEDICO')
        
        # Filtrar áreas según el tipo de centro del usuario
        if hasattr(self.request.user, 'perfil') and self.request.user.perfil.centro_salud:
            tipo_centro = self.request.user.perfil.centro_salud.tipo
            form.fields['area'].queryset = Area.objects.filter(categoria__tipo=tipo_centro)
        
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = get_object_or_404(Paciente, pk=self.kwargs['pk'])
        context['paciente'] = paciente
        
        # Verificar estado del paciente
        if hasattr(paciente, 'ficha_medica'):
            estado_actual = paciente.ficha_medica.estado
            context['estado_paciente'] = dict(FichaMedica.ESTADOS_PACIENTE)[estado_actual]
            context['puede_ingresar'] = estado_actual == 'EN_ALTA'
        else:
            context['puede_ingresar'] = True
        
        return context
    
    def form_valid(self, form):
        paciente = get_object_or_404(Paciente, pk=self.kwargs['pk'])
        ficha, created = FichaMedica.objects.get_or_create(paciente=paciente)
        
        # Validar que el paciente esté en alta antes de crear nuevo ingreso
        if not created and ficha.estado != 'EN_ALTA':
            estado_display = dict(FichaMedica.ESTADOS_PACIENTE)[ficha.estado]
            messages.error(
                self.request,
                f'No se puede registrar un nuevo ingreso. El paciente {paciente.nombre} {paciente.apellido1} '
                f'tiene un registro activo en estado: {estado_display}. '
                f'Debe estar en "En Alta" para permitir un nuevo ingreso.'
            )
            return redirect('admission_dashboard')
        
        # Actualizar estado a en tratamiento
        ficha.estado = 'EN_TRATAMIENTO'
        ficha.save()
        
        form.instance.ficha_medica = ficha
        messages.success(self.request, f'Ingreso registrado para {paciente.nombre} {paciente.apellido1}.')
        return super().form_valid(form)
