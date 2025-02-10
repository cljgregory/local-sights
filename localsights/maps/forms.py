from django import forms
from .models import *
from django.forms import ModelForm

modes = (
    ("driving", "driving"), 
    ("walking", "walking"),
    ("bicycling", "bicycling"),
    ("transit", "transit")
)

class createMapForm(forms.Form):
    class Meta:
        model = Map
        fields = '__all__'



class DistanceForm(ModelForm): 
    from_location = forms.ModelChoiceField(label="Location from", required=True, queryset=Location.objects.all())
    to_location = forms.ModelChoiceField(label="Location to", required=True, queryset=Location.objects.all())
    mode = forms.ChoiceField(choices=modes, required=True)
    class Meta: 
        model = Distances
        exclude = ['created_at', 'edited_at', 'distance_km','duration_mins','duration_traffic_mins']
