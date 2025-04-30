from django.db import models

class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    max_capacity = models.IntegerField()
    
    def __str__(self):
        return self.name

class RoomPhoto(models.Model):
    room_type = models.ForeignKey(RoomType, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='room_photos/')
    description = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"Photo for {self.room_type.name}"

class Equipment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Room(models.Model):
    number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, related_name='rooms', on_delete=models.CASCADE)
    floor = models.IntegerField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    equipment = models.ManyToManyField(Equipment, related_name='rooms')
    
    def __str__(self):
        return f"Room {self.number} - {self.room_type.name}"
    
    def calculate_price(self, start_date, end_date):
        """Calcule le prix pour une période donnée"""
        # Implémentation basique - prix de base * nombre de jours
        days = (end_date - start_date).days
        if days <= 0:
            days = 1
        return self.base_price * days