from django import forms
from .models import Room, RoomType, Equipment, RoomPhoto

class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = ['name', 'description', 'max_capacity']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class RoomPhotoForm(forms.ModelForm):
    class Meta:
        model = RoomPhoto
        fields = ['image', 'description']

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class RoomForm(forms.ModelForm):
    equipment = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Room
        fields = ['number', 'room_type', 'floor', 'base_price', 'is_available', 'description', 'equipment']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class AvailabilitySearchForm(forms.Form):
    check_in_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    check_out_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    guests = forms.IntegerField(min_value=1, initial=1)
    room_type = forms.ModelChoiceField(
        queryset=RoomType.objects.all(),
        required=False,
        empty_label="Tous les types de chambre"
    )