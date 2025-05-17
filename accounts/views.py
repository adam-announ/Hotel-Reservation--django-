from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.contrib.auth import logout
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
def dashboard_router(request):
    """Redirige vers le tableau de bord approprié en fonction du rôle de l'utilisateur"""
    
    # Par défaut, rediriger vers le tableau de bord client
    dashboard_template = 'dashboard.html'
    context = {}
    
    # Vérifier si l'utilisateur a un profil avec un rôle
    if hasattr(request.user, 'profile') and request.user.profile.role:
        role_name = request.user.profile.role.name
        
        if role_name == 'Administrateur':
            dashboard_template = 'accounts/admin_dashboard.html'
            # Ajouter des statistiques pour le tableau de bord admin
            context.update({
                'total_users': User.objects.count(),
                'active_rooms': 40,  # Remplacer par de vraies données
                'monthly_reservations': 156,
                'monthly_revenue': 42500
            })
        
        elif role_name == 'Manager':
            dashboard_template = 'accounts/manager_dashboard.html'
            # Ajouter des statistiques pour le tableau de bord manager
            context.update({
                'occupancy_rate': 78,
                'monthly_revenue': 42500,
                'monthly_reservations': 156,
                'client_satisfaction': 4.7
            })
        
        elif role_name == 'Réceptionniste':
            dashboard_template = 'accounts/receptionist_dashboard.html'
            # Ajouter des statistiques pour le tableau de bord réceptionniste
            from datetime import date
            context.update({
                'today_date': date.today(),
                'today_checkins_count': 8,
                'today_checkouts_count': 5,
                'available_rooms_count': 15,
                'occupancy_rate': 78
            })
    
    return render(request, dashboard_template, context)

@login_required
def user_list(request):
    # Vérifier si l'utilisateur a le droit de voir la liste des utilisateurs
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette page.")
        return redirect('dashboard')
    
    users = User.objects.all().select_related('profile__role')
    roles = Role.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users, 'roles': roles})

@login_required
def user_detail(request, pk):
    # Vérifier si l'utilisateur a le droit de voir les détails d'un utilisateur
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette page.")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/user_detail.html', {'user': user})

# Nouvelle fonction pour créer un utilisateur
@login_required
def user_create(request):
    # Vérifier si l'utilisateur a le droit de créer des utilisateurs
    if not request.user.profile.role or request.user.profile.role.name != 'Administrateur':
        messages.error(request, "Vous n'avez pas l'autorisation de créer des utilisateurs.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role_id = request.POST.get('role')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        is_active = request.POST.get('is_active') == 'on'
        
        # Vérifier si les mots de passe correspondent
        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            roles = Role.objects.all()
            users = User.objects.all().select_related('profile__role')
            return render(request, 'accounts/user_list.html', {'users': users, 'roles': roles})
        
        # Vérifier si le nom d'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà utilisé.")
            roles = Role.objects.all()
            users = User.objects.all().select_related('profile__role')
            return render(request, 'accounts/user_list.html', {'users': users, 'roles': roles})
        
        try:
            # Utiliser une transaction pour garantir l'intégrité des données
            with transaction.atomic():
                # Créer l'utilisateur
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=is_active
                )
                
                # Mettre à jour le profil
                role = Role.objects.get(id=role_id)
                profile = Profile.objects.get(user=user)
                profile.role = role
                profile.phone = phone
                profile.save()
                
                # Si le rôle est client, créer un client seulement s'il n'existe pas déjà
                if role.name == 'Client':
                    if not Client.objects.filter(profile=profile).exists():
                        client = Client.objects.create(
                            profile=profile,
                            address=address
                        )
            
            messages.success(request, f"L'utilisateur {username} a été créé avec succès.")
            return redirect('user_list')
        except IntegrityError as e:
            messages.error(request, f"Erreur lors de la création de l'utilisateur: {str(e)}")
            roles = Role.objects.all()
            users = User.objects.all().select_related('profile__role')
            return render(request, 'accounts/user_list.html', {'users': users, 'roles': roles})
    
    # Pour les requêtes GET, rediriger vers user_list
    users = User.objects.all().select_related('profile__role')
    roles = Role.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users, 'roles': roles})

# Nouvelle fonction pour mettre à jour un utilisateur
@login_required
def user_update(request, pk):
    # Vérifier si l'utilisateur a le droit de modifier des utilisateurs
    if not request.user.profile.role or request.user.profile.role.name != 'Administrateur':
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des utilisateurs.")
        return redirect('dashboard')
    
    user_to_update = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        role_id = request.POST.get('role')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        is_active = request.POST.get('is_active') == 'True'
        
        try:
            # Utiliser une transaction pour garantir l'intégrité des données
            with transaction.atomic():
                # Mettre à jour l'utilisateur
                user_to_update.first_name = first_name
                user_to_update.last_name = last_name
                user_to_update.email = email
                user_to_update.is_active = is_active
                user_to_update.save()
                
                # Mettre à jour le profil
                role = Role.objects.get(id=role_id)
                user_to_update.profile.role = role
                user_to_update.profile.phone = phone
                user_to_update.profile.save()
                
                # Gérer le client si nécessaire
                if role.name == 'Client':
                    client, created = Client.objects.get_or_create(profile=user_to_update.profile)
                    client.address = address
                    client.save()
            
            messages.success(request, f"L'utilisateur {user_to_update.username} a été mis à jour avec succès.")
            return redirect('user_list')
        except IntegrityError as e:
            messages.error(request, f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}")
            roles = Role.objects.all()
            return render(request, 'accounts/user_edit.html', {
                'user_item': user_to_update,
                'roles': roles
            })
    
    roles = Role.objects.all()
    return render(request, 'accounts/user_edit.html', {
        'user_item': user_to_update,
        'roles': roles
    })

# Nouvelle fonction pour supprimer un utilisateur
@login_required
def user_delete(request, pk):
    # Vérifier si l'utilisateur a le droit de supprimer des utilisateurs
    if not request.user.profile.role or request.user.profile.role.name != 'Administrateur':
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des utilisateurs.")
        return redirect('dashboard')
    
    user_to_delete = get_object_or_404(User, pk=pk)
    
    # Empêcher la suppression de son propre compte
    if user_to_delete == request.user:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('user_list')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                username = user_to_delete.username
                user_to_delete.delete()
                messages.success(request, f"L'utilisateur {username} a été supprimé avec succès.")
        except IntegrityError as e:
            messages.error(request, f"Erreur lors de la suppression de l'utilisateur: {str(e)}")
        return redirect('user_list')
    
    return render(request, 'accounts/user_confirm_delete.html', {'user': user_to_delete})

@login_required
def manage_roles(request):
    # Vérifier si l'utilisateur a le droit de gérer les rôles
    if not request.user.profile.role or request.user.profile.role.name != 'Administrateur':
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette page.")
        return redirect('dashboard')
    
    roles = Role.objects.all()
    # Ajouter un message de débogage pour vérifier si des rôles sont récupérés
    print(f"Nombre de rôles récupérés : {roles.count()}")
    
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

@login_required
def delete_role(request, pk):
    # Vérifier si l'utilisateur a le droit de supprimer des rôles
    if not request.user.profile.role or request.user.profile.role.name != 'Administrateur':
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des rôles.")
        return redirect('dashboard')
    
    role = get_object_or_404(Role, pk=pk)
    
    # Empêcher la suppression des rôles essentiels
    if role.name in ['Administrateur', 'Manager', 'Réceptionniste', 'Client']:
        messages.error(request, "Vous ne pouvez pas supprimer ce rôle essentiel.")
        return redirect('manage_roles')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                role_name = role.name
                role.delete()
                messages.success(request, f"Le rôle {role_name} a été supprimé avec succès.")
        except IntegrityError as e:
            messages.error(request, f"Erreur lors de la suppression du rôle : {str(e)}")
        return redirect('manage_roles')
    
    return render(request, 'accounts/role_confirm_delete.html', {'role': role})

@login_required
def switch_role(request, role_id):
    """
    Permet à un utilisateur administrateur de changer temporairement de rôle
    pour tester différentes vues et fonctionnalités
    """
    # Vérifier si l'utilisateur est un administrateur
    if not request.user.profile.role or request.user.profile.role.name != 'Administrateur':
        messages.error(request, "Vous n'avez pas l'autorisation de changer de rôle.")
        return redirect('dashboard')
    
    # Enregistrer le rôle actuel dans la session si ce n'est pas déjà fait
    if 'original_role_id' not in request.session:
        request.session['original_role_id'] = request.user.profile.role.id
    
    # Changer le rôle de l'utilisateur
    new_role = get_object_or_404(Role, pk=role_id)
    request.user.profile.role = new_role
    request.user.profile.save()
    
    messages.success(request, f"Vous utilisez maintenant le rôle: {new_role.name}")
    return redirect('dashboard')

@login_required
def restore_role(request):
    """Restaure le rôle original de l'administrateur"""
    if 'original_role_id' in request.session:
        original_role = get_object_or_404(Role, pk=request.session['original_role_id'])
        request.user.profile.role = original_role
        request.user.profile.save()
        
        # Supprimer l'information de rôle original de la session
        del request.session['original_role_id']
        
        messages.success(request, "Votre rôle original a été restauré.")
    return redirect('dashboard')

@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "Vous avez été déconnecté avec succès.")
        return redirect('home')
    else:
        return render(request, 'accounts/logout.html')