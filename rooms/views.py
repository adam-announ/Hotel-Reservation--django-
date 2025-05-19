from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
import json  # Ajouté pour la conversion en JSON
from .models import Room, RoomType, Equipment, RoomPhoto
from .forms import RoomForm, RoomTypeForm, EquipmentForm, RoomPhotoForm, AvailabilitySearchForm
from reservations.models import Reservation, ReservationStatus

def room_list(request):
    """Affiche la liste des chambres disponibles"""
    room_types = RoomType.objects.all()
    rooms = Room.objects.all()
    
    # Filtrage par type de chambre
    room_type_id = request.GET.get('room_type')
    if room_type_id:
        rooms = rooms.filter(room_type_id=room_type_id)
    
    # Filtrage par capacité
    capacity = request.GET.get('capacity')
    if capacity:
        rooms = rooms.filter(room_type__max_capacity__gte=capacity)
    
    # Filtrage par prix maximum
    price = request.GET.get('price')
    if price:
        rooms = rooms.filter(base_price__lte=price)
    
    # Filtrage par disponibilité
    availability = request.GET.get('available')
    if availability == 'yes':
        rooms = rooms.filter(is_available=True)
    elif availability == 'no':
        rooms = rooms.filter(is_available=False)
    
    context = {
        'rooms': rooms,
        'room_types': room_types,
        'selected_type': room_type_id,
        'availability': availability
    }
    
    return render(request, 'rooms/room_list.html', context)

def room_detail(request, pk):
    """Affiche les détails d'une chambre"""
    room = get_object_or_404(Room, pk=pk)
    
    # Obtenir les photos du type de chambre
    photos = room.room_type.photos.all()
    
    # Vérifier la disponibilité pour les 30 prochains jours
    upcoming_reservations = Reservation.objects.filter(
        rooms=room,
        status__in=[ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN],
        check_out_date__gte=datetime.now().date()
    ).order_by('check_in_date')[:5]
    
    # Déterminer si l'utilisateur connecté est un administrateur ou manager
    is_admin_or_manager = False
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and request.user.profile.role:
            is_admin_or_manager = request.user.profile.role.name in ['Administrateur', 'Manager']
    
    context = {
        'room': room,
        'photos': photos,
        'upcoming_reservations': upcoming_reservations,
        'is_admin_or_manager': is_admin_or_manager
    }
    
    return render(request, 'rooms/room_detail.html', context)

@login_required
def room_create(request):
    """Crée une nouvelle chambre"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter une chambre.")
        return redirect('room_list')
    
    # Préparez les données des types de chambres pour JavaScript
    room_types_data = {}
    for rt in RoomType.objects.all():
        equipment_ids = []
        if hasattr(rt, 'equipment'):
            try:
                equipment_ids = list(rt.equipment.values_list('id', flat=True))
            except:
                pass
        
        room_types_data[rt.id] = {
            'base_price': float(rt.base_price),
            'description': rt.description,
            'equipment_ids': equipment_ids
        }
    
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save()
            
            # Gérer les équipements si ce n'est pas configuré automatiquement
            equipment = form.cleaned_data.get('equipment')
            if equipment:
                room.equipment.set(equipment)
                
            messages.success(request, 'Chambre créée avec succès!')
            return redirect('room_list')
    else:
        form = RoomForm()
    
    return render(request, 'rooms/room_form.html', {
        'form': form, 
        'title': 'Ajouter une chambre',
        'room_types_data': json.dumps(room_types_data)  # Convertir en JSON pour JavaScript
    })

@login_required
def room_update(request, pk):
    """Met à jour une chambre existante"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de modifier une chambre.")
        return redirect('room_list')
    
    room = get_object_or_404(Room, pk=pk)
    
    # Préparez les données des types de chambres pour JavaScript
    room_types_data = {}
    for rt in RoomType.objects.all():
        equipment_ids = []
        if hasattr(rt, 'equipment'):
            try:
                equipment_ids = list(rt.equipment.values_list('id', flat=True))
            except:
                pass
        
        room_types_data[rt.id] = {
            'base_price': float(rt.base_price),
            'description': rt.description,
            'equipment_ids': equipment_ids
        }
    
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            room = form.save()
            
            # Gérer les équipements si ce n'est pas configuré automatiquement
            equipment = form.cleaned_data.get('equipment')
            if equipment:
                room.equipment.set(equipment)
                
            messages.success(request, 'Chambre mise à jour avec succès!')
            return redirect('room_detail', pk=room.pk)
    else:
        form = RoomForm(instance=room)
    
    return render(request, 'rooms/room_form.html', {
        'form': form, 
        'title': 'Modifier la chambre', 
        'room': room,
        'room_types_data': json.dumps(room_types_data)  # Convertir en JSON pour JavaScript
    })

@login_required
def room_delete(request, pk):
    """Supprime une chambre"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer une chambre.")
        return redirect('room_list')
    
    room = get_object_or_404(Room, pk=pk)
    
    # Vérifier si la chambre a des réservations
    reservations = room.reservations.all()
    
    if request.method == 'POST':
        room_number = room.number
        try:
            room.delete()
            messages.success(request, f'La chambre {room_number} a été supprimée avec succès!')
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression de la chambre: {str(e)}")
        return redirect('room_list')
    
    return render(request, 'rooms/room_confirm_delete.html', {'room': room, 'reservations': reservations})

def search_availability(request):
    """Recherche les chambres disponibles pour une période donnée"""
    available_rooms = []
    
    if request.method == 'POST':
        form = AvailabilitySearchForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in_date']
            check_out = form.cleaned_data['check_out_date']
            guests = form.cleaned_data['guests']
            room_type = form.cleaned_data['room_type']
            
            # Obtenir toutes les chambres
            rooms = Room.objects.filter(is_available=True)
            
            # Filtrer par type de chambre si spécifié
            if room_type:
                rooms = rooms.filter(room_type=room_type)
            
            # Filtrer par capacité
            rooms = rooms.filter(room_type__max_capacity__gte=guests)
            
            # Exclure les chambres déjà réservées pour cette période
            reserved_rooms = Reservation.objects.filter(
                Q(check_in_date__lte=check_out) & Q(check_out_date__gte=check_in),
                status__in=[ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN]
            ).values_list('rooms__id', flat=True)
            
            available_rooms = rooms.exclude(id__in=reserved_rooms)
            
            # Stocker la recherche dans la session pour la réservation
            request.session['search'] = {
                'check_in': check_in.isoformat(),
                'check_out': check_out.isoformat(),
                'guests': guests
            }
    else:
        # Si on a un room_id dans les paramètres, on le pré-sélectionne
        room_id = request.GET.get('room_id')
        initial_data = {}
        
        if room_id:
            room = get_object_or_404(Room, id=room_id)
            initial_data = {
                'room_type': room.room_type,
                'guests': room.room_type.max_capacity
            }
        
        form = AvailabilitySearchForm(initial=initial_data)
    
    context = {
        'form': form,
        'available_rooms': available_rooms
    }
    
    return render(request, 'rooms/availability_search.html', context)

@login_required
def room_type_list(request):
    """Liste tous les types de chambres"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette page.")
        return redirect('room_list')
    
    room_types = RoomType.objects.all()
    equipments = Equipment.objects.all()
    return render(request, 'rooms/room_type_list.html', {'room_types': room_types, 'equipments': equipments})

@login_required
def room_type_create(request):
    """Crée un nouveau type de chambre"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter un type de chambre.")
        return redirect('room_list')
    
    if request.method == 'POST':
        # Récupérer directement les données du formulaire
        name = request.POST.get('name')
        description = request.POST.get('description')
        max_capacity = request.POST.get('max_capacity')
        base_price = request.POST.get('price')  # Modifié ici pour correspondre au nom du champ
        
        # Vérifier que les données requises sont présentes
        if not name or not max_capacity or not base_price:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            equipments = Equipment.objects.all()
            return render(request, 'rooms/room_type_form.html', {
                'title': 'Ajouter un type de chambre',
                'equipments': equipments
            })
        
        try:
            # Créer le type de chambre
            room_type = RoomType.objects.create(
                name=name,
                description=description,
                max_capacity=int(max_capacity),
                base_price=float(base_price)
            )
            
            # Gérer les équipements s'ils sont soumis dans le formulaire et si le modèle possède l'attribut equipment
            if hasattr(room_type, 'equipment'):
                equipment_ids = request.POST.getlist('equipment')
                if equipment_ids:
                    equipment = Equipment.objects.filter(id__in=equipment_ids)
                    room_type.equipment.set(equipment)
            
            messages.success(request, f'Type de chambre "{name}" créé avec succès!')
            return redirect('room_type_list')
            
        except ValueError:
            messages.error(request, "Les valeurs numériques sont incorrectes. Veuillez vérifier la capacité et le prix.")
            equipments = Equipment.objects.all()
            return render(request, 'rooms/room_type_form.html', {
                'title': 'Ajouter un type de chambre',
                'equipments': equipments
            })
        except Exception as e:
            messages.error(request, f"Erreur lors de la création du type de chambre: {str(e)}")
            return redirect('room_type_list')
    
    # Si la méthode est GET, afficher le formulaire
    equipments = Equipment.objects.all()
    return render(request, 'rooms/room_type_form.html', {
        'title': 'Ajouter un type de chambre',
        'equipments': equipments
    })

@login_required
def room_type_update(request, pk):
    """Met à jour un type de chambre existant"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de modifier un type de chambre.")
        return redirect('room_type_list')
    
    room_type = get_object_or_404(RoomType, pk=pk)
    
    if request.method == 'POST':
        # Récupérer directement les données du formulaire
        name = request.POST.get('name')
        description = request.POST.get('description')
        max_capacity = request.POST.get('max_capacity')
        base_price = request.POST.get('price')  # Modifié ici pour correspondre au nom du champ
        
        # Vérifier que les données requises sont présentes
        if not name or not max_capacity or not base_price:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            equipments = Equipment.objects.all()
            return render(request, 'rooms/room_type_form.html', {
                'title': 'Modifier le type de chambre',
                'room_type': room_type,
                'equipments': equipments
            })
        
        try:
            # Mettre à jour le type de chambre
            room_type.name = name
            room_type.description = description
            room_type.max_capacity = int(max_capacity)
            room_type.base_price = float(base_price)
            room_type.save()
            
            # Gérer les équipements s'ils sont soumis dans le formulaire et si le modèle possède l'attribut equipment
            if hasattr(room_type, 'equipment'):
                equipment_ids = request.POST.getlist('equipment')
                if equipment_ids:
                    equipment = Equipment.objects.filter(id__in=equipment_ids)
                    room_type.equipment.set(equipment)
                else:
                    room_type.equipment.clear()
            
            messages.success(request, f'Type de chambre "{name}" mis à jour avec succès!')
            return redirect('room_type_list')
            
        except ValueError:
            messages.error(request, "Les valeurs numériques sont incorrectes. Veuillez vérifier la capacité et le prix.")
            equipments = Equipment.objects.all()
            return render(request, 'rooms/room_type_form.html', {
                'title': 'Modifier le type de chambre',
                'room_type': room_type,
                'equipments': equipments
            })
        except Exception as e:
            messages.error(request, f"Erreur lors de la mise à jour du type de chambre: {str(e)}")
            return redirect('room_type_list')
    
    # Si la méthode est GET, afficher le formulaire pré-rempli
    equipments = Equipment.objects.all()
    return render(request, 'rooms/room_type_form.html', {
        'title': 'Modifier le type de chambre',
        'room_type': room_type,
        'equipments': equipments
    })

@login_required
def room_type_delete(request, pk):
    """Supprime un type de chambre"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer un type de chambre.")
        return redirect('room_type_list')
    
    room_type = get_object_or_404(RoomType, pk=pk)
    
    # Vérifier si des chambres utilisent ce type
    if room_type.rooms.exists():
        messages.error(request, "Ce type de chambre ne peut pas être supprimé car il est utilisé par des chambres.")
        return redirect('room_type_list')
    
    if request.method == 'POST':
        room_type_name = room_type.name
        try:
            room_type.delete()
            messages.success(request, f'Le type de chambre "{room_type_name}" a été supprimé avec succès!')
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression du type de chambre: {str(e)}")
        return redirect('room_type_list')
    
    return render(request, 'rooms/room_type_confirm_delete.html', {'room_type': room_type})

@login_required
def manage_equipment(request):
    """Gère les équipements des chambres"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de gérer les équipements.")
        return redirect('room_list')
    
    equipments = Equipment.objects.all()
    
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Équipement ajouté avec succès!')
            return redirect('manage_equipment')
    else:
        form = EquipmentForm()
    
    return render(request, 'rooms/equipment_list.html', {'equipments': equipments, 'form': form})

@login_required
def equipment_update(request, pk):
    """Met à jour un équipement existant"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de modifier un équipement.")
        return redirect('manage_equipment')
    
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if not name:
            messages.error(request, "Le nom de l'équipement est requis.")
            return redirect('manage_equipment')
            
        try:
            equipment.name = name
            equipment.description = description
            equipment.save()
            messages.success(request, f'Équipement "{name}" mis à jour avec succès!')
        except Exception as e:
            messages.error(request, f"Erreur lors de la mise à jour de l'équipement: {str(e)}")
        
    return redirect('manage_equipment')

@login_required
def equipment_delete(request, pk):
    """Supprime un équipement"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer un équipement.")
        return redirect('manage_equipment')
    
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        name = equipment.name
        try:
            # Vérifier si l'équipement est utilisé par des chambres
            if equipment.rooms.exists():
                messages.warning(request, f"L'équipement '{name}' est utilisé par des chambres. Suppression annulée.")
                return redirect('manage_equipment')
                
            equipment.delete()
            messages.success(request, f'Équipement "{name}" supprimé avec succès!')
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression de l'équipement: {str(e)}")
        
    return redirect('manage_equipment')

@login_required
def add_room_photo(request, room_type_id):
    """Ajoute une photo à un type de chambre"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter des photos.")
        return redirect('room_type_list')
    
    room_type = get_object_or_404(RoomType, pk=room_type_id)
    
    if request.method == 'POST':
        form = RoomPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.room_type = room_type
            photo.save()
            messages.success(request, 'Photo ajoutée avec succès!')
            return redirect('room_type_detail', pk=room_type_id)
    else:
        form = RoomPhotoForm()
    
    return render(request, 'rooms/room_photo_form.html', {
        'form': form, 
        'room_type': room_type,
        'title': 'Ajouter une photo'
    })

@login_required
def delete_room_photo(request, pk):
    """Supprime une photo de type de chambre"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des photos.")
        return redirect('room_type_list')
    
    photo = get_object_or_404(RoomPhoto, pk=pk)
    room_type_id = photo.room_type.id
    
    if request.method == 'POST':
        try:
            photo.delete()
            messages.success(request, 'Photo supprimée avec succès!')
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression de la photo: {str(e)}")
        
        return redirect('room_type_detail', pk=room_type_id)
    
    return render(request, 'rooms/room_photo_confirm_delete.html', {'photo': photo})