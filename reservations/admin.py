from django.contrib import admin
from .models import Reservation, Payment, Service, ReservationStatus, PaymentMethod

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    readonly_fields = ('payment_date',)
    fields = ('amount', 'payment_method', 'reference', 'is_confirmed', 'payment_date')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'check_in_date', 'check_out_date', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'check_in_date', 'check_out_date')
    search_fields = ('client__profile__user__username', 'client__profile__user__first_name', 'client__profile__user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('rooms', 'services')
    inlines = [PaymentInline]
    
    fieldsets = (
        ('Client et dates', {
            'fields': ('client', 'check_in_date', 'check_out_date', 'status')
        }),
        ('Chambres et services', {
            'fields': ('rooms', 'services')
        }),
        ('Détails financiers', {
            'fields': ('total_amount',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Informations système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('client__profile__user').prefetch_related('rooms', 'services')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'reservation', 'amount', 'payment_method', 'payment_date', 'is_confirmed')
    list_filter = ('payment_method', 'is_confirmed', 'payment_date')
    search_fields = ('reservation__client__profile__user__username', 'reference')
    readonly_fields = ('payment_date',)
    
    fieldsets = (
        ('Réservation', {
            'fields': ('reservation',)
        }),
        ('Détails du paiement', {
            'fields': ('amount', 'payment_method', 'reference', 'is_confirmed')
        }),
        ('Date', {
            'fields': ('payment_date',)
        }),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available', 'description')
    list_filter = ('is_available',)
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_available')