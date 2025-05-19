from django.contrib import admin
from .models import Room, RoomType, Equipment, RoomPhoto

class RoomPhotoInline(admin.TabularInline):
    model = RoomPhoto
    extra = 1

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_capacity', 'get_rooms_count')
    search_fields = ('name', 'description')
    inlines = [RoomPhotoInline]
    
    def get_rooms_count(self, obj):
        return obj.rooms.count()
    get_rooms_count.short_description = 'Nombre de chambres'

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'room_type', 'floor', 'base_price', 'is_available')
    list_filter = ('is_available', 'room_type', 'floor')
    search_fields = ('number', 'description')
    filter_horizontal = ('equipment',)
    list_editable = ('is_available', 'base_price')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('number', 'room_type', 'floor', 'is_available')
        }),
        ('Tarification', {
            'fields': ('base_price',)
        }),
        ('Caractéristiques', {
            'fields': ('description', 'equipment')
        }),
    )

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(RoomPhoto)
class RoomPhotoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'room_type', 'description')
    list_filter = ('room_type',)
    search_fields = ('description', 'room_type__name')