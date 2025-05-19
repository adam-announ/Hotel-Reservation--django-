# reservations/forms.py (mise à jour)

from django import forms
from django.contrib.auth.models import User
from .models import Reservation, Payment, Service, ReservationStatus
from accounts.models import Client
from rooms.models import Room

class ReservationForm(forms.ModelForm):
    """Formulaire pour créer/modifier une réservation"""
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Si l'utilisateur est un membre du personnel, permettre la sélection du client
        if user and hasattr(user, 'profile') and user.profile.role and user.profile.role.name in ['Administrateur', 'Manager', 'Réceptionniste']:
            # Afficher tous les clients pour le personnel
            self.fields['client'] = forms.ModelChoiceField(
                queryset=Client.objects.all(),
                widget=forms.Select(attrs={'class': 'form-select'}),
                empty_label="Sélectionnez un client"
            )
            self.fields['client'].label_from_instance = lambda obj: f"{obj.profile.user.get_full_name()} ({obj.profile.user.email})"
        else:
            # Pour les clients, masquer le champ client (sera défini automatiquement)
            if 'client' in self.fields:
                del self.fields['client']
        
        # Filtrer les chambres disponibles
        self.fields['rooms'].queryset = Room.objects.filter(is_available=True)
        
        # Styliser les champs
        self.fields['check_in_date'].widget.attrs.update({
            'class': 'form-control',
            'type': 'date'
        })
        self.fields['check_out_date'].widget.attrs.update({
            'class': 'form-control',
            'type': 'date'
        })
        self.fields['notes'].widget.attrs.update({
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notes ou demandes spéciales...'
        })
    
    class Meta:
        model = Reservation
        fields = ['client', 'check_in_date', 'check_out_date', 'rooms', 'services', 'notes']
        widgets = {
            'rooms': forms.CheckboxSelectMultiple(),
            'services': forms.CheckboxSelectMultiple(),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        
        if check_in_date and check_out_date:
            if check_out_date <= check_in_date:
                raise forms.ValidationError("La date de départ doit être postérieure à la date d'arrivée.")
        
        return cleaned_data

class QuickReservationForm(forms.ModelForm):
    """Formulaire simplifié pour créer rapidement une réservation (réceptionniste)"""
    
    client_email = forms.EmailField(
        label="Email du client",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text="Entrez l'email du client existant ou créez un nouveau client"
    )
    
    client_first_name = forms.CharField(
        max_length=30,
        label="Prénom",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    client_last_name = forms.CharField(
        max_length=30,
        label="Nom",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    client_phone = forms.CharField(
        max_length=20,
        label="Téléphone",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    selected_room = forms.ModelChoiceField(
        queryset=Room.objects.filter(is_available=True),
        label="Chambre",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Sélectionnez une chambre"
    )
    
    class Meta:
        model = Reservation
        fields = ['check_in_date', 'check_out_date', 'notes']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_client_email(self):
        email = self.cleaned_data['client_email']
        if not User.objects.filter(email=email).exists():
            # Vérifier si les informations du nouveau client sont fournies
            if not self.cleaned_data.get('client_first_name') or not self.cleaned_data.get('client_last_name'):
                raise forms.ValidationError("Pour un nouveau client, veuillez fournir le prénom et le nom.")
        return email

class PaymentForm(forms.ModelForm):
    """Formulaire pour enregistrer un paiement"""
    
    def __init__(self, *args, **kwargs):
        reservation = kwargs.pop('reservation', None)
        super().__init__(*args, **kwargs)
        
        if reservation:
            # Calculer le montant restant à payer
            existing_payments = Payment.objects.filter(reservation=reservation, is_confirmed=True)
            total_paid = sum(payment.amount for payment in existing_payments)
            balance = reservation.total_amount - total_paid
            
            # Pré-remplir le montant avec le solde restant
            self.fields['amount'].initial = balance
            self.fields['amount'].widget.attrs.update({
                'max': balance,
                'step': '0.01'
            })
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'reference']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01'
            }),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Référence de transaction (optionnel)'
            }),
        }

class ReservationStatusForm(forms.ModelForm):
    """Formulaire pour changer le statut d'une réservation"""
    
    class Meta:
        model = Reservation
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }

class ServiceForm(forms.ModelForm):
    """Formulaire pour gérer les services"""
    
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CheckInForm(forms.Form):
    """Formulaire pour le check-in"""
    
    confirmation = forms.BooleanField(
        required=True,
        label="Je confirme que tous les documents ont été vérifiés et que la chambre est prête",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    notes = forms.CharField(
        required=False,
        label="Notes (optionnel)",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notes sur le check-in...'
        })
    )

class CheckOutForm(forms.Form):
    """Formulaire pour le check-out"""
    
    room_condition = forms.ChoiceField(
        choices=[
            ('GOOD', 'Bon état'),
            ('NEEDS_CLEANING', 'Nettoyage nécessaire'),
            ('NEEDS_MAINTENANCE', 'Maintenance nécessaire'),
        ],
        label="État de la chambre",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    extra_charges = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        label="Frais supplémentaires (€)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        })
    )
    
    extra_charges_reason = forms.CharField(
        required=False,
        label="Raison des frais supplémentaires",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minibar, dommages, etc.'
        })
    )
    
    notes = forms.CharField(
        required=False,
        label="Notes (optionnel)",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notes sur le check-out...'
        })
    )
    
    force_checkout = forms.BooleanField(
        required=False,
        label="Forcer le check-out malgré un solde impayé",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )