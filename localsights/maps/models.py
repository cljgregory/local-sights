from django.db import models

# Create your models here.

from django.urls import reverse  # To generate URLS by reversing URL patterns
import uuid # Required for unique location instances


class Location(models.Model):
    name = models.CharField(max_length=500)
    creator = models.CharField(
        max_length=200,
        unique=False,
        help_text="",
        default=''
    )
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    zipcode = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    edited_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    lat = models.DecimalField(max_digits = 9, decimal_places = 6, blank=True, null=True) 
    lng = models.DecimalField(max_digits = 9, decimal_places = 6, blank=True, null=True) 
    place_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse('location-detail', args=[str(self.id)])
    
    def __eq__(self, other): 
        if isinstance(other, Location): 
            if other.name == self.name and self.address == other.address and self.city == other.city and self.zipcode == other.zipcode: 
                return True
        return False
    
    def __hash__(self):
        return super().__hash__()
    
class Map(models.Model):

    name = models.CharField(
        max_length=200,
        unique=False,
        help_text="",
        default=''
    )

    creator = models.CharField(
        max_length=200,
        unique=False,
        help_text="",
        default=''
    )

    starting_location = models.ForeignKey(Location, on_delete=models.CASCADE, default='', null=True, related_name='firstlocation')
    dest_location = models.ForeignKey(Location, on_delete=models.CASCADE, default='', null=True, related_name='lastlocation')

    locations = models.ManyToManyField(
        'Location',
        related_name='locations'
    )

    date = models.DateField()

    zoom_level = models.FloatField()

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse('map-detail', args=[str(self.id)])
    
class Distances (models.Model):
    from_location = models.ForeignKey(Location, related_name = 'from_location', on_delete=models.CASCADE)
    to_location = models.ForeignKey(Location, related_name = 'to_location', on_delete=models.CASCADE)
    mode = models.CharField(max_length=200, blank=True, null=True)
    distance_km = models.DecimalField(max_digits=10, decimal_places=2)
    duration_mins = models.DecimalField(max_digits=10, decimal_places=2)
    duration_traffic_mins = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    edited_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id

