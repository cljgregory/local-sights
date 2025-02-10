import django_filters

from .models import *

class LocationFilter(django_filters.FilterSet):
    class Meta:
        model = Location
        fields = ['name', 'zipcode', 'city']
        