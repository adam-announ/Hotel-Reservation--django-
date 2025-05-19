from django.shortcuts import render
from rooms.models import Room, RoomType

def home_view(request):
    """Vue de la page d'accueil"""
    # Récupérer tous les types de chambres
    room_types = RoomType.objects.all().distinct()
    
    # Récupérer une chambre représentative pour chaque type de chambre
    featured_rooms = []
    for room_type in room_types:
        # Chercher une chambre disponible de ce type
        room = Room.objects.filter(room_type=room_type, is_available=True).first()
        if room:
            featured_rooms.append(room)
    
    context = {
        'featured_rooms': featured_rooms,
        'room_types': room_types,
    }
    
    return render(request, 'home.html', context)

