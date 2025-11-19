from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from login.views import views
from login.forms import CustomLoginForm

urlpatterns = [
    path('', LoginView.as_view(template_name='login/index.html', authentication_form=CustomLoginForm), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('home/', views.home, name='home'),
    
    # Rutas de recovery password
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/done/', TemplateView.as_view(template_name='login/password_reset_done.html'), name='password_reset_done'), 
    path('password-reset/confirm/<uuid:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', TemplateView.as_view(template_name='login/password_reset_complete.html'), name='password_reset_complete'), 
]
