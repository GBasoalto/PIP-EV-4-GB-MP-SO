
from django.urls import path
from centrosalud.views.views import DashboardView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
]
