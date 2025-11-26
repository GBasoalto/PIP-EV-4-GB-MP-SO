
from django.urls import path
from centrosalud.views.views import DashboardView
from centrosalud.views import doctor_views, director_views, admission_views

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # Doctor URLs
    path('doctor/patients/', doctor_views.DoctorPatientListView.as_view(), name='doctor_patient_list'),
    path('doctor/patient/<int:pk>/', doctor_views.PatientDetailView.as_view(), name='patient_detail'),
    path('doctor/atencion/<int:pk>/update/', doctor_views.UpdateAtencionMedicaView.as_view(), name='update_atencion'),
    path('doctor/patient/<int:pk>/update-status/', doctor_views.UpdatePatientStatusView.as_view(), name='update_patient_status'),

    # Director URLs
    path('director/dashboard/', director_views.DirectorDashboardView.as_view(), name='director_dashboard'),

    # Admission URLs
    path('admission/dashboard/', admission_views.AdmissionDashboardView.as_view(), name='admission_dashboard'),
    path('admission/search/', admission_views.SearchOrCreatePatientView.as_view(), name='search_patient'),
    path('admission/create/<str:rut>/', admission_views.CreatePatientWithAdmissionView.as_view(), name='create_patient_with_rut'),
    path('admission/register/<int:pk>/', admission_views.RegisterAdmissionView.as_view(), name='register_admission'),
]
