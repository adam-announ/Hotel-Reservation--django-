from django import forms
from .models import Room, RoomType, Equipment, RoomPhoto

class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = ['name', 'description', 'max_capacity', 'base_price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'max_capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.01}),
        }

class RoomPhotoForm(forms.ModelForm):
    class Meta:
        model = RoomPhoto
        fields = ['image', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class RoomForm(forms.ModelForm):
    equipment = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Room
        fields = ['number', 'room_type', 'floor', 'base_price', 'is_available', 'description', 'equipment', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.01}),
            'room_type': forms.Select(attrs={'class': 'form-select'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AvailabilitySearchForm(forms.Form):
    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    guests = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1})
    )
    room_type = forms.ModelChoiceField(
        queryset=RoomType.objects.all(),
        required=False,
        empty_label="Tous les types de chambre",
        widget=forms.Select(attrs={'class': 'form-select'})
    )