from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('logout/', views.logout_view, name='logout'),  # Utilise votre vue personnalisée
    path('profile/', views.profile, name='profile'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    # Ajoutez cette ligne pour résoudre l'erreur
    path('users/create/', views.user_create, name='user_create'),
    # Ajoutez également cette ligne pour l'action de mise à jour
    path('users/<int:pk>/update/', views.user_update, name='user_update'),
    # Et celle-ci pour la suppression
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('roles/', views.manage_roles, name='manage_roles'),
    path('roles/<int:pk>/edit/', views.edit_role, name='edit_role'),
    # Ajoutez cette ligne pour la suppression des rôles
    path('roles/<int:pk>/delete/', views.delete_role, name='delete_role'),
    
    # URLs pour le changement de rôle (pour les administrateurs)
    path('switch-role/<int:role_id>/', views.switch_role, name='switch_role'),
    path('restore-role/', views.restore_role, name='restore_role'),
    
     # Réinitialisation de mot de passe
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]