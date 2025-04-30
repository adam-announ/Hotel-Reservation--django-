from django import forms
from .models import Reservation, Payment, Service, ReservationStatus, PaymentMethod
from accounts.models import Client
from rooms.models import Room

class ReservationForm(forms.ModelForm):
    rooms = forms.ModelMultipleChoiceField(
        queryset=Room.objects.filter(is_available=True),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.filter(is_available=True),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    check_in_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    check_out_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = Reservation
        fields = ['client', 'rooms', 'check_in_date', 'check_out_date', 'services', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and not user.is_staff:
            # Seulement pour les clients, préremplir et désactiver le champ client
            try:
                client = Client.objects.get(profile__user=user)
                self.fields['client'].initial = client
                self.fields['client'].disabled = True
            except Client.DoesNotExist:
                pass

    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        
        if check_in_date and check_out_date:
            if check_in_date >= check_out_date:
                raise forms.ValidationError("La date de départ doit être postérieure à la date d'arrivée.")
        
        return cleaned_data

class ReservationStatusForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['status']
        widgets = {
            'status': forms.Select(choices=ReservationStatus.choices),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'reference']
        widgets = {
            'payment_method': forms.Select(choices=PaymentMethod.choices),
        }
    
    def __init__(self, *args, **kwargs):
        reservation = kwargs.pop('reservation', None)
        super().__init__(*args, **kwargs)
        
        if reservation:
            self.fields['amount'].initial = reservation.total_amount
            self.fields['amount'].help_text = f"Montant total de la réservation: {reservation.total_amount} €"
            self.reservation = reservation
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if hasattr(self, 'reservation') and amount > self.reservation.total_amount:
            raise forms.ValidationError("Le montant ne peut pas dépasser le total de la réservation.")
        return amount

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }