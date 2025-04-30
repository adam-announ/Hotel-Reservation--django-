from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
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
    
    context = {
        'room': room,
        'photos': photos,
        'upcoming_reservations': upcoming_reservations
    }
    
    return render(request, 'rooms/room_detail.html', context)

@login_required
def room_create(request):
    """Crée une nouvelle chambre"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter une chambre.")
        return redirect('room_list')
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chambre créée avec succès!')
            return redirect('room_list')
    else:
        form = RoomForm()
    
    return render(request, 'rooms/room_form.html', {'form': form, 'title': 'Ajouter une chambre'})

@login_required
def room_update(request, pk):
    """Met à jour une chambre existante"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de modifier une chambre.")
        return redirect('room_list')
    
    room = get_object_or_404(Room, pk=pk)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chambre mise à jour avec succès!')
            return redirect('room_detail', pk=room.pk)
    else:
        form = RoomForm(instance=room)
    
    return render(request, 'rooms/room_form.html', {'form': form, 'title': 'Modifier la chambre'})

@login_required
def room_delete(request, pk):
    """Supprime une chambre"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer une chambre.")
        return redirect('room_list')
    
    room = get_object_or_404(Room, pk=pk)
    
    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Chambre supprimée avec succès!')
        return redirect('room_list')
    
    return render(request, 'rooms/room_confirm_delete.html', {'room': room})

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
        form = AvailabilitySearchForm()
    
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
    return render(request, 'rooms/room_type_list.html', {'room_types': room_types})

@login_required
def room_type_create(request):
    """Crée un nouveau type de chambre"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter un type de chambre.")
        return redirect('room_list')
    
    if request.method == 'POST':
        form = RoomTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Type de chambre créé avec succès!')
            return redirect('room_type_list')
    else:
        form = RoomTypeForm()
    
    return render(request, 'rooms/room_type_form.html', {'form': form, 'title': 'Ajouter un type de chambre'})

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