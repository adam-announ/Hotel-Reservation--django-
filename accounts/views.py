from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import (
    CustomUserCreationForm, 
    ProfileUpdateForm, 
    UserUpdateForm, 
    ClientUpdateForm,
    EmployeeForm, 
    RoleForm
)
from .models import Profile, Client, Employee, Role, Permission

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Compte créé avec succès!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        # Vérifier si l'utilisateur est un client
        try:
            client = Client.objects.get(profile=request.user.profile)
            client_form = ClientUpdateForm(request.POST, instance=client)
            forms_valid = user_form.is_valid() and profile_form.is_valid() and client_form.is_valid()
            
            if forms_valid:
                user_form.save()
                profile_form.save()
                client_form.save()
                messages.success(request, 'Votre profil a été mis à jour!')
                return redirect('profile')
        except Client.DoesNotExist:
            forms_valid = user_form.is_valid() and profile_form.is_valid()
            
            if forms_valid:
                user_form.save()
                profile_form.save()
                messages.success(request, 'Votre profil a été mis à jour!')
                return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        
        try:
            client = Client.objects.get(profile=request.user.profile)
            client_form = ClientUpdateForm(instance=client)
            return render(request, 'accounts/profile.html', {
                'user_form': user_form,
                'profile_form': profile_form,
                'client_form': client_form,
                'is_client': True
            })
        except Client.DoesNotExist:
            return render(request, 'accounts/profile.html', {
                'user_form': user_form,
                'profile_form': profile_form,
                'is_client': False
            })

@login_required
def user_list(request):
    # Vérifier si l'utilisateur a le droit de voir la liste des utilisateurs
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette page.")
        return redirect('dashboard')
    
    users = User.objects.all().select_related('profile__role')
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
def user_detail(request, pk):
    # Vérifier si l'utilisateur a le droit de voir les détails d'un utilisateur
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette page.")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/user_detail.html', {'user': user})

@login_required
def manage_roles(request):
    # Vérifier si l'utilisateur a le droit de gérer les rôles
    if not request.user.profile.role or request.user.profile.role.name != 'Administrateur':
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette page.")
        return redirect('dashboard')
    
    roles = Role.objects.all()
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rôle créé avec succès!')
            return redirect('manage_roles')
    else:
        form = RoleForm()
    
    return render(request, 'accounts/manage_roles.html', {'roles': roles, 'form': form})

@login_required
def edit_role(request, pk):
    # Vérifier si l'utilisateur a le droit de modifier les rôles
    if not request.user.profile.role or request.user.profile.role.name != 'Administrateur':
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette page.")
        return redirect('dashboard')
    
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rôle mis à jour avec succès!')
            return redirect('manage_roles')
    else:
        form = RoleForm(instance=role)
    
    return render(request, 'accounts/edit_role.html', {'form': form, 'role': role})