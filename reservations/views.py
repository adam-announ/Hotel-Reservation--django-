from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
import json
from accounts.models import Client
from rooms.models import Room
from .models import Reservation, Payment, Service, ReservationStatus
from .forms import ReservationForm, PaymentForm, ServiceForm, ReservationStatusForm

@login_required
def reservation_list(request):
    """Affiche la liste des réservations de l'utilisateur ou toutes les réservations pour le personnel"""
    # Déterminer si l'utilisateur est un client ou un employé
    is_staff = request.user.profile.role and request.user.profile.role.name in ['Administrateur', 'Manager', 'Réceptionniste']
    
    if is_staff:
        # Personnel: afficher toutes les réservations avec filtres
        reservations = Reservation.objects.all().order_by('-created_at')
        
        # Filtrer par statut si spécifié
        status = request.GET.get('status')
        if status:
            reservations = reservations.filter(status=status)
        
        # Filtrer par date si spécifié
        date_filter = request.GET.get('date_filter')
        if date_filter == 'today':
            today = timezone.now().date()
            reservations = reservations.filter(
                Q(check_in_date=today) | Q(check_out_date=today)
            )
        elif date_filter == 'upcoming':
            today = timezone.now().date()
            reservations = reservations.filter(check_in_date__gt=today)
        elif date_filter == 'past':
            today = timezone.now().date()
            reservations = reservations.filter(check_out_date__lt=today)
    else:
        # Client: afficher uniquement ses réservations
        try:
            client = Client.objects.get(profile__user=request.user)
            reservations = Reservation.objects.filter(client=client).order_by('-created_at')
        except Client.DoesNotExist:
            messages.error(request, "Votre profil client n'est pas configuré correctement.")
            return redirect('dashboard')
    
    context = {
        'reservations': reservations,
        'is_staff': is_staff,
        'statuses': ReservationStatus.choices,
        'selected_status': request.GET.get('status', ''),
        'date_filter': request.GET.get('date_filter', '')
    }
    
    return render(request, 'reservations/reservation_list.html', context)

@login_required
def reservation_detail(request, pk):
    """Affiche les détails d'une réservation"""
    reservation = get_object_or_404(Reservation, pk=pk)
    
    # Vérifier si l'utilisateur a le droit de voir cette réservation
    is_staff = request.user.profile.role and request.user.profile.role.name in ['Administrateur', 'Manager', 'Réceptionniste']
    is_owner = hasattr(request.user.profile, 'client') and request.user.profile.client == reservation.client
    
    if not (is_staff or is_owner):
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette réservation.")
        return redirect('reservation_list')
    
    # Obtenir les paiements liés à cette réservation
    payments = Payment.objects.filter(reservation=reservation)
    total_paid = sum(payment.amount for payment in payments if payment.is_confirmed)
    balance = reservation.total_amount - total_paid
    
    # Pour le changement de statut (uniquement pour le personnel)
    if is_staff:
        if request.method == 'POST':
            status_form = ReservationStatusForm(request.POST, instance=reservation)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, 'Statut de la réservation mis à jour!')
                return redirect('reservation_detail', pk=reservation.pk)
        else:
            status_form = ReservationStatusForm(instance=reservation)
    else:
        status_form = None
    
    context = {
        'reservation': reservation,
        'payments': payments,
        'total_paid': total_paid,
        'balance': balance,
        'is_staff': is_staff,
        'status_form': status_form
    }
    
    return render(request, 'reservations/reservation_detail.html', context)

@login_required
def create_reservation(request):
    """Crée une nouvelle réservation"""
    # Obtenir les données de recherche de disponibilité depuis la session
    search_data = request.session.get('search', None)
    initial_data = {}
    
    if search_data:
        initial_data['check_in_date'] = datetime.fromisoformat(search_data['check_in'])
        initial_data['check_out_date'] = datetime.fromisoformat(search_data['check_out'])
    
    # Obtenir l'ID de la chambre depuis les paramètres d'URL
    room_id = request.GET.get('room_id')
    selected_rooms = []
    
    if room_id:
        try:
            selected_rooms = [Room.objects.get(id=room_id)]
        except Room.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = ReservationForm(request.POST, user=request.user)
        if form.is_valid():
            reservation = form.save(commit=False)
            
            # Si l'utilisateur est un client, définir automatiquement le client
            if not request.user.is_staff:
                try:
                    client = Client.objects.get(profile__user=request.user)
                    reservation.client = client
                except Client.DoesNotExist:
                    messages.error(request, "Votre profil client n'est pas configuré correctement.")
                    return redirect('dashboard')
            
            # Calculer le montant total
            rooms = form.cleaned_data['rooms']
            services = form.cleaned_data['services']
            
            # Enregistrer d'abord pour créer l'ID
            reservation.save()
            
            # Ensuite ajouter les relations many-to-many
            reservation.rooms.set(rooms)
            reservation.services.set(services)
            
            # Calculer et mettre à jour le montant total
            reservation.total_amount = reservation.calculate_total()
            reservation.save()
            
            messages.success(request, 'Réservation créée avec succès!')
            
            # Rediriger vers le paiement
            return redirect('create_payment', reservation_id=reservation.id)
    else:
        form = ReservationForm(user=request.user, initial=initial_data)
        if selected_rooms:
            form.fields['rooms'].initial = selected_rooms
    
    return render(request, 'reservations/reservation_form.html', {'form': form})

@login_required
def create_payment(request, reservation_id):
    """Ajoute un paiement à une réservation"""
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    
    # Vérifier si l'utilisateur a le droit d'ajouter un paiement
    is_staff = request.user.profile.role and request.user.profile.role.name in ['Administrateur', 'Manager', 'Réceptionniste']
    is_owner = hasattr(request.user.profile, 'client') and request.user.profile.client == reservation.client
    
    if not (is_staff or is_owner):
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
        return redirect('reservation_list')
    
    # Calculer le solde restant
    existing_payments = Payment.objects.filter(reservation=reservation, is_confirmed=True)
    total_paid = sum(payment.amount for payment in existing_payments)
    balance = reservation.total_amount - total_paid
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, reservation=reservation)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.reservation = reservation
            
            # Simuler une confirmation de paiement (dans un système réel, cela passerait par un service de paiement)
            # Pour le moment, tous les paiements sont automatiquement confirmés
            payment.is_confirmed = True
            payment.save()
            
            # Mettre à jour le statut de la réservation si entièrement payée
            new_total_paid = total_paid + payment.amount
            if new_total_paid >= reservation.total_amount:
                reservation.status = ReservationStatus.CONFIRMED
                reservation.save()
            
            messages.success(request, 'Paiement effectué avec succès!')
            
            # Rediriger vers la confirmation de réservation
            return redirect('reservation_confirmation', pk=reservation.id)
    else:
        # Préremplir le montant avec le solde restant
        form = PaymentForm(reservation=reservation, initial={'amount': balance})
    
    context = {
        'form': form,
        'reservation': reservation,
        'total_paid': total_paid,
        'balance': balance
    }
    
    return render(request, 'reservations/payment_form.html', context)

@login_required
def reservation_confirmation(request, pk):
    """Affiche la confirmation d'une réservation"""
    reservation = get_object_or_404(Reservation, pk=pk)
    
    # Vérifier si l'utilisateur a le droit de voir cette réservation
    is_staff = request.user.profile.role and request.user.profile.role.name in ['Administrateur', 'Manager', 'Réceptionniste']
    is_owner = hasattr(request.user.profile, 'client') and request.user.profile.client == reservation.client
    
    if not (is_staff or is_owner):
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette réservation.")
        return redirect('reservation_list')
    
    # Obtenir les paiements liés à cette réservation
    payments = Payment.objects.filter(reservation=reservation, is_confirmed=True)
    total_paid = sum(payment.amount for payment in payments)
    
    context = {
        'reservation': reservation,
        'payments': payments,
        'total_paid': total_paid
    }
    
    return render(request, 'reservations/reservation_confirmation.html', context)

@login_required
def cancel_reservation(request, pk):
    """Annule une réservation"""
    reservation = get_object_or_404(Reservation, pk=pk)
    
    # Vérifier si l'utilisateur a le droit d'annuler cette réservation
    is_staff = request.user.profile.role and request.user.profile.role.name in ['Administrateur', 'Manager', 'Réceptionniste']
    is_owner = hasattr(request.user.profile, 'client') and request.user.profile.client == reservation.client
    
    if not (is_staff or is_owner):
        messages.error(request, "Vous n'avez pas l'autorisation d'annuler cette réservation.")
        return redirect('reservation_list')
    
    # Vérifier si la réservation peut être annulée
    if reservation.status in [ReservationStatus.CHECKED_IN, ReservationStatus.CHECKED_OUT]:
        messages.error(request, "Cette réservation ne peut plus être annulée.")
        return redirect('reservation_detail', pk=reservation.pk)
    
    if request.method == 'POST':
        reservation.status = ReservationStatus.CANCELLED
        reservation.save()
        messages.success(request, 'Réservation annulée avec succès!')
        return redirect('reservation_list')
    
    return render(request, 'reservations/reservation_cancel.html', {'reservation': reservation})

@login_required
def check_in(request, pk):
    """Effectue le check-in d'une réservation"""
    # Vérifier si l'utilisateur est un membre du personnel
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager', 'Réceptionniste']:
        messages.error(request, "Vous n'avez pas l'autorisation d'effectuer cette action.")
        return redirect('reservation_list')
    
    reservation = get_object_or_404(Reservation, pk=pk)
    
    # Vérifier si la réservation peut faire l'objet d'un check-in
    if reservation.status != ReservationStatus.CONFIRMED:
        messages.error(request, "Cette réservation ne peut pas faire l'objet d'un check-in.")
        return redirect('reservation_detail', pk=reservation.pk)
    
    if request.method == 'POST':
        reservation.status = ReservationStatus.CHECKED_IN
        reservation.save()
        messages.success(request, 'Check-in effectué avec succès!')
        return redirect('reservation_detail', pk=reservation.pk)
    
    return render(request, 'reservations/check_in.html', {'reservation': reservation})

@login_required
def check_out(request, pk):
    """Effectue le check-out d'une réservation"""
    # Vérifier si l'utilisateur est un membre du personnel
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager', 'Réceptionniste']:
        messages.error(request, "Vous n'avez pas l'autorisation d'effectuer cette action.")
        return redirect('reservation_list')
    
    reservation = get_object_or_404(Reservation, pk=pk)
    
    # Vérifier si la réservation peut faire l'objet d'un check-out
    if reservation.status != ReservationStatus.CHECKED_IN:
        messages.error(request, "Cette réservation ne peut pas faire l'objet d'un check-out.")
        return redirect('reservation_detail', pk=reservation.pk)
    
    if request.method == 'POST':
        reservation.status = ReservationStatus.CHECKED_OUT
        reservation.save()
        messages.success(request, 'Check-out effectué avec succès!')
        return redirect('reservation_detail', pk=reservation.pk)
    
    return render(request, 'reservations/check_out.html', {'reservation': reservation})

@login_required
def manage_services(request):
    """Gère les services additionnels"""
    # Vérifier si l'utilisateur est un membre du personnel
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
        return redirect('dashboard')
    
    services = Service.objects.all()
    
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service ajouté avec succès!')
            return redirect('manage_services')
    else:
        form = ServiceForm()
    
    return render(request, 'reservations/service_list.html', {'services': services, 'form': form})