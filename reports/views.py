from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, F, Q
from django.http import HttpResponse
from django.utils import timezone
import csv
from datetime import datetime, timedelta
from accounts.models import Client, Employee
from rooms.models import Room, RoomType
from reservations.models import Reservation, Payment, ReservationStatus
from .models import Report, ReportType

@login_required
def report_list(request):
    """Affiche la liste des rapports générés"""
    # Vérifier si l'utilisateur a les droits d'accès
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
        return redirect('dashboard')
    
    reports = Report.objects.all().order_by('-date_generated')
    
    context = {
        'reports': reports,
        'report_types': ReportType.choices
    }
    
    return render(request, 'reports/report_list.html', context)

@login_required
def report_detail(request, pk):
    """Affiche les détails d'un rapport enregistré"""
    # Vérifier si l'utilisateur a les droits d'accès
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
        return redirect('dashboard')
    
    report = get_object_or_404(Report, pk=pk)
    
    context = {
        'report': report
    }
    
    return render(request, 'reports/report_detail.html', context)

@login_required
def report_delete(request, pk):
    """Supprime un rapport"""
    # Vérifier si l'utilisateur a la permission
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer ce rapport.")
        return redirect('dashboard')
    
    report = get_object_or_404(Report, pk=pk)
    
    if request.method == 'POST':
        report_title = report.title
        report.delete()
        messages.success(request, f'Le rapport "{report_title}" a été supprimé avec succès!')
        return redirect('report_list')
    
    return render(request, 'reports/report_confirm_delete.html', {'report': report})

@login_required
def occupancy_report(request):
    """Génère un rapport d'occupation"""
    # Vérifier si l'utilisateur a les droits d'accès
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
        return redirect('dashboard')
    
    # Paramètres de date par défaut (30 derniers jours)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Obtenir les dates depuis le formulaire si soumis
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Calculer le nombre total de chambres
    total_rooms = Room.objects.count()
    
    # Calculer les réservations par jour
    days = (end_date - start_date).days + 1
    occupancy_data = []
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        # Compter les réservations actives ce jour-là
        reservations_count = Reservation.objects.filter(
            check_in_date__lte=current_date,
            check_out_date__gt=current_date,
            status__in=[ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN]
        ).count()
        
        # Compter le nombre de chambres réservées (peut être différent du nombre de réservations)
        rooms_reserved = Reservation.objects.filter(
            check_in_date__lte=current_date,
            check_out_date__gt=current_date,
            status__in=[ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN]
        ).values('rooms').distinct().count()
        
        # Calculer le taux d'occupation
        occupancy_rate = (rooms_reserved / total_rooms * 100) if total_rooms > 0 else 0
        
        occupancy_data.append({
            'date': current_date,
            'reservations': reservations_count,
            'rooms_reserved': rooms_reserved,
            'occupancy_rate': round(occupancy_rate, 2)
        })
    
    # Calculer les statistiques d'occupation par type de chambre
    room_types = RoomType.objects.all()
    room_type_stats = []
    
    for room_type in room_types:
        rooms_count = Room.objects.filter(room_type=room_type).count()
        
        # Compter les réservations pour ce type de chambre
        reservations_count = Reservation.objects.filter(
            rooms__room_type=room_type,
            check_in_date__lte=end_date,
            check_out_date__gte=start_date,
            status__in=[ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN, ReservationStatus.CHECKED_OUT]
        ).count()
        
        room_type_stats.append({
            'room_type': room_type,
            'rooms_count': rooms_count,
            'reservations_count': reservations_count
        })
    
    # Statistiques globales
    avg_occupancy = sum(day['occupancy_rate'] for day in occupancy_data) / days if days > 0 else 0
    max_occupancy = max(day['occupancy_rate'] for day in occupancy_data) if occupancy_data else 0
    min_occupancy = min(day['occupancy_rate'] for day in occupancy_data) if occupancy_data else 0
    
    # Calculer le taux d'occupation moyen par jour de la semaine
    weekday_stats = [0] * 7
    weekday_counts = [0] * 7
    
    for day in occupancy_data:
        weekday = day['date'].weekday()
        weekday_stats[weekday] += day['occupancy_rate']
        weekday_counts[weekday] += 1
    
    weekday_avg = []
    for i in range(7):
        avg = weekday_stats[i] / weekday_counts[i] if weekday_counts[i] > 0 else 0
        weekday_name = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][i]
        weekday_avg.append({'day': weekday_name, 'avg_rate': round(avg, 2)})
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_rooms': total_rooms,
        'occupancy_data': occupancy_data,
        'room_type_stats': room_type_stats,
        'avg_occupancy': round(avg_occupancy, 2),
        'max_occupancy': round(max_occupancy, 2),
        'min_occupancy': round(min_occupancy, 2),
        'weekday_avg': weekday_avg
    }
    
    # Enregistrer le rapport si demandé
    if 'save_report' in request.POST:
        try:
            employee = Employee.objects.get(profile__user=request.user)
            
            # Préparer le contenu du rapport
            content = f"""
            Rapport d'occupation du {start_date} au {end_date}
            
            Statistiques globales:
            - Taux d'occupation moyen: {round(avg_occupancy, 2)}%
            - Taux d'occupation maximum: {round(max_occupancy, 2)}%
            - Taux d'occupation minimum: {round(min_occupancy, 2)}%
            - Nombre total de chambres: {total_rooms}
            
            Statistiques par type de chambre:
            {', '.join([f"{stat['room_type'].name}: {stat['reservations_count']} réservations" for stat in room_type_stats])}
            
            Taux d'occupation moyen par jour de la semaine:
            {', '.join([f"{day['day']}: {day['avg_rate']}%" for day in weekday_avg])}
            """
            
            # Créer le rapport
            Report.objects.create(
                title=f"Rapport d'occupation {start_date} - {end_date}",
                report_type=ReportType.OCCUPANCY,
                content=content,
                generated_by=employee,
                start_date=start_date,
                end_date=end_date
            )
            
            messages.success(request, 'Rapport enregistré avec succès!')
        except Employee.DoesNotExist:
            messages.error(request, "Votre profil employé n'est pas configuré correctement.")
    
    # Exporter en CSV si demandé
    if 'export_csv' in request.POST:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="occupancy_report_{start_date}_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Réservations', 'Chambres réservées', 'Taux d\'occupation (%)'])
        
        for day in occupancy_data:
            writer.writerow([
                day['date'],
                day['reservations'],
                day['rooms_reserved'],
                day['occupancy_rate']
            ])
        
        return response
    
    return render(request, 'reports/occupancy_report.html', context)

@login_required
def revenue_report(request):
    """Génère un rapport des revenus"""
    # Vérifier si l'utilisateur a les droits d'accès
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
        return redirect('dashboard')
    
    # Paramètres de date par défaut (30 derniers jours)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Obtenir les dates depuis le formulaire si soumis
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Calculer les revenus par jour
    days = (end_date - start_date).days + 1
    revenue_data = []
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        # Calculer les revenus des paiements confirmés ce jour-là
        daily_revenue = Payment.objects.filter(
            payment_date__date=current_date,
            is_confirmed=True
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        revenue_data.append({
            'date': current_date,
            'revenue': daily_revenue
        })
    
    # Calculer les revenus par méthode de paiement
    payment_methods = Payment.objects.filter(
        payment_date__date__gte=start_date,
        payment_date__date__lte=end_date,
        is_confirmed=True
    ).values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    # Calculer les revenus par type de chambre
    room_type_revenue = Reservation.objects.filter(
        check_in_date__lte=end_date,
        check_out_date__gte=start_date,
        status__in=[ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN, ReservationStatus.CHECKED_OUT]
    ).values('rooms__room_type__name').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    )
    
    # Statistiques globales
    total_revenue = sum(day['revenue'] for day in revenue_data)
    avg_daily_revenue = total_revenue / days if days > 0 else 0
    max_daily_revenue = max(day['revenue'] for day in revenue_data) if revenue_data else 0
    
    # Calculer le chiffre d'affaires moyen par jour de la semaine
    weekday_revenue = [0] * 7
    weekday_counts = [0] * 7
    
    for day in revenue_data:
        weekday = day['date'].weekday()
        weekday_revenue[weekday] += day['revenue']
        weekday_counts[weekday] += 1
    
    weekday_avg_revenue = []
    for i in range(7):
        avg = weekday_revenue[i] / weekday_counts[i] if weekday_counts[i] > 0 else 0
        weekday_name = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][i]
        weekday_avg_revenue.append({'day': weekday_name, 'avg_revenue': round(avg, 2)})
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'revenue_data': revenue_data,
        'payment_methods': payment_methods,
        'room_type_revenue': room_type_revenue,
        'total_revenue': total_revenue,
        'avg_daily_revenue': round(avg_daily_revenue, 2),
        'max_daily_revenue': max_daily_revenue,
        'weekday_avg_revenue': weekday_avg_revenue
    }
    
    # Enregistrer le rapport si demandé
    if 'save_report' in request.POST:
        try:
            employee = Employee.objects.get(profile__user=request.user)
            
            # Préparer le contenu du rapport
            content = f"""
            Rapport de revenus du {start_date} au {end_date}
            
            Statistiques globales:
            - Revenu total: {total_revenue} €
            - Revenu quotidien moyen: {round(avg_daily_revenue, 2)} €
            - Revenu quotidien maximum: {max_daily_revenue} €
            
            Revenus par méthode de paiement:
            {', '.join([f"{method['payment_method']}: {method['total']} € ({method['count']} paiements)" for method in payment_methods])}
            
            Revenus par type de chambre:
            {', '.join([f"{room['rooms__room_type__name']}: {room['total']} € ({room['count']} réservations)" for room in room_type_revenue])}
            
            Revenus moyens par jour de la semaine:
            {', '.join([f"{day['day']}: {day['avg_revenue']} €" for day in weekday_avg_revenue])}
            """
            
            # Créer le rapport
            Report.objects.create(
                title=f"Rapport de revenus {start_date} - {end_date}",
                report_type=ReportType.REVENUE,
                content=content,
                generated_by=employee,
                start_date=start_date,
                end_date=end_date
            )
            
            messages.success(request, 'Rapport enregistré avec succès!')
        except Employee.DoesNotExist:
            messages.error(request, "Votre profil employé n'est pas configuré correctement.")
    
    # Exporter en CSV si demandé
    if 'export_csv' in request.POST:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="revenue_report_{start_date}_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Revenu (€)'])
        
        for day in revenue_data:
            writer.writerow([
                day['date'],
                day['revenue']
            ])
        
        return response
    
    return render(request, 'reports/revenue_report.html', context)

@login_required
def client_stats(request):
    """Génère des statistiques sur les clients"""
    # Vérifier si l'utilisateur a les droits d'accès
    if not request.user.profile.role or request.user.profile.role.name not in ['Administrateur', 'Manager']:
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
        return redirect('dashboard')
    
    # Paramètres de date par défaut (dernier an)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    # Obtenir les dates depuis le formulaire si soumis
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Statistiques globales sur les clients
    total_clients = Client.objects.count()
    active_clients = Client.objects.filter(reservations__check_in_date__gte=start_date).distinct().count()
    
    # Top 10 des clients par nombre de réservations
    top_clients_by_reservations = Client.objects.filter(
        reservations__check_in_date__gte=start_date,
        reservations__check_in_date__lte=end_date
    ).annotate(
        reservations_count=Count('reservations'),
        total_spent=Sum('reservations__total_amount')
    ).order_by('-reservations_count')[:10]
    
    # Top 10 des clients par montant dépensé
    top_clients_by_spending = Client.objects.filter(
        reservations__check_in_date__gte=start_date,
        reservations__check_in_date__lte=end_date
    ).annotate(
        reservations_count=Count('reservations'),
        total_spent=Sum('reservations__total_amount')
    ).order_by('-total_spent')[:10]
    
    # Statistiques sur la durée moyenne de séjour
    avg_stay_duration = Reservation.objects.filter(
        check_in_date__gte=start_date,
        check_in_date__lte=end_date,
        status__in=[ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN, ReservationStatus.CHECKED_OUT]
    ).annotate(
        duration=F('check_out_date') - F('check_in_date')
    ).aggregate(avg_duration=Avg('duration'))
    
    # Convertir le résultat en jours (si disponible)
    avg_stay_days = 0
    if avg_stay_duration['avg_duration']:
        avg_stay_days = avg_stay_duration['avg_duration'].days
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_clients': total_clients,
        'active_clients': active_clients,
        'top_clients_by_reservations': top_clients_by_reservations,
        'top_clients_by_spending': top_clients_by_spending,
        'avg_stay_days': avg_stay_days
    }
    
    # Enregistrer le rapport si demandé
    if 'save_report' in request.POST:
        try:
            employee = Employee.objects.get(profile__user=request.user)
            
            # Préparer le contenu du rapport
            content = f"""
            Rapport statistiques clients du {start_date} au {end_date}
            
            Statistiques globales:
            - Nombre total de clients: {total_clients}
            - Clients actifs sur la période: {active_clients}
            - Durée moyenne de séjour: {avg_stay_days} jours
            
            Top clients par nombre de réservations:
            {', '.join([f"{client.profile.user.get_full_name()}: {client.reservations_count} réservations" for client in top_clients_by_reservations[:5]])}
            
            Top clients par montant dépensé:
            {', '.join([f"{client.profile.user.get_full_name()}: {client.total_spent} €" for client in top_clients_by_spending[:5]])}
            """
            
            # Créer le rapport
            Report.objects.create(
                title=f"Rapport clients {start_date} - {end_date}",
                report_type=ReportType.CLIENT_STATS,
                content=content,
                generated_by=employee,
                start_date=start_date,
                end_date=end_date
            )
            
            messages.success(request, 'Rapport enregistré avec succès!')
        except Employee.DoesNotExist:
            messages.error(request, "Votre profil employé n'est pas configuré correctement.")
    
    # Exporter en CSV si demandé
    if 'export_csv' in request.POST:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="client_stats_{start_date}_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Client', 'Email', 'Nombre de réservations', 'Montant total dépensé (€)', 'Date d\'inscription'])
        
        # Tous les clients avec leurs statistiques
        all_clients = Client.objects.filter(
            reservations__check_in_date__gte=start_date,
            reservations__check_in_date__lte=end_date
        ).annotate(
            reservations_count=Count('reservations'),
            total_spent=Sum('reservations__total_amount')
        ).order_by('-total_spent')
        
        for client in all_clients:
            writer.writerow([
                f"{client.profile.user.get_full_name()}",
                client.profile.user.email,
                client.reservations_count,
                client.total_spent or 0,
                client.profile.date_joined.date()
            ])
        
        return response
    
    return render(request, 'reports/client_stats.html', context)