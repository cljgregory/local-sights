import json
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
import googlemaps
from django.conf import settings
from .forms import *
from datetime import datetime
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
import requests
from .models import __eq__

class HomeView(ListView):
    template_name = "pages/home.html"
    context_object_name = 'mydata'
    model = Location
    success_url = "/"


class GeocodingView(View):
    template_name = "pages/geocoding.html"

    def get(self,request,pk): 
        location = Location.objects.get(pk=pk)

        if location.lng and location.lat and location.place_id != None: 
            lat = location.lat
            lng = location.lng
            place_id = location.place_id
            label = "from my database"

        if location.address and location.country and location.zipcode and location.city != None: 
            address_string = str(location.address)+", "+str(location.zipcode)+", "+str(location.city)+", "+str(location.country)
            key = getattr(settings, 'GOOGLE_API_KEY', None)
            gmaps = googlemaps.Client(key)
            result = gmaps.geocode(address_string)[0]
            
            lat = result.get('geometry', {}).get('location', {}).get('lat', None)
            lng = result.get('geometry', {}).get('location', {}).get('lng', None)
            place_id = result.get('place_id', {})
            label = "from my api call"
            location.lat = lat
            location.lng =  lng
            location.place_id = place_id
            location.save()

        else: 
            result = ""
            lat = ""
            lng = ""
            place_id = ""
            label = "no call made"


        context = {
            'result':result,
            'location':location,
            'lat':lat, 
            'lng':lng, 
            'place_id':place_id, 
            'label':label
        }
        
        return render(request, self.template_name, context)
    
class DistanceView(View):
    template_name = "pages/distance.html"

    def get(self, request): 
        form = DistanceForm
        distances = Distances.objects.all()
        context = {
            'form':form,
            'distances':distances
        }

        return render(request, self.template_name, context)

    def post(self, request): 
        form = DistanceForm(request.POST)
        if form.is_valid(): 
            from_location = form.cleaned_data['from_location']
            from_location_info = Location.objects.get(name=from_location)
            from_address_string = str(from_location_info.address)+", "+str(from_location_info.zipcode)+", "+str(from_location_info.city)+", "+str(from_location_info.country)

            to_location = form.cleaned_data['to_location']
            to_location_info = Location.objects.get(name=to_location)
            to_address_string = str(to_location_info.address)+", "+str(to_location_info.zipcode)+", "+str(to_location_info.city)+", "+str(to_location_info.country)

            mode = form.cleaned_data['mode']
            now = datetime.now()
            key = getattr(settings, 'GOOGLE_API_KEY', None)
            gmaps = googlemaps.Client(key)
            calculate = gmaps.distance_matrix(
                    from_address_string,
                    to_address_string,
                    mode = mode,
                    departure_time = now
            )


            duration_seconds = calculate['rows'][0]['elements'][0]['duration']['value']
            duration_minutes = duration_seconds/60

            distance_meters = calculate['rows'][0]['elements'][0]['distance']['value']
            distance_kilometers = distance_meters/1000

            if 'duration_in_traffic' in calculate['rows'][0]['elements'][0]: 
                duration_in_traffic_seconds = calculate['rows'][0]['elements'][0]['duration_in_traffic']['value']
                duration_in_traffic_minutes = duration_in_traffic_seconds/60
            else: 
                duration_in_traffic_minutes = None

            
            obj = Distances(
                from_location = Location.objects.get(name=from_location),
                to_location = Location.objects.get(name=to_location),
                mode = mode,
                distance_km = distance_kilometers,
                duration_mins = duration_minutes,
                duration_traffic_mins = duration_in_traffic_minutes
            )

            obj.save()

        else: 
            print(form.errors)
        
        return redirect('distance')
    
class DisplayMapView(View): 
    template_name = "pages/display_map.html"
    apikey = getattr(settings, 'GOOGLE_API_KEY', None)
    def get(self,request): 
        context = {
            "key": DisplayMapView.apikey
        }

        return render(request, self.template_name, context)
    
class LocationListView(ListView):
    model = Location
    template_name = "pages/locations.html"
    
    def get_queryset(self):
        return (
            Location.objects.filter(creator=self.request.user)
        )

class LocationDetailView(DetailView):
    model = Location
    template_name = "locations/location_detail.html"

    def get(self, request, pk):
        location = Location.objects.get(pk=pk)
        
        
        # Once we have the address use it to get latitude and longitude from the API 
        if (location.address and location.country and location.zipcode and location.city != None) and (location.lat == None or location.lng == None or location.place_id == None): 
            print("here in detail view")
            address_string = str(location.address)+", "+str(location.zipcode)+", "+str(location.city)+", "+str(location.country)
            key = getattr(settings, 'GOOGLE_API_KEY', None)
            gmaps = googlemaps.Client(key)
            result = gmaps.geocode(address_string)[0]
            
            location.lat = result.get('geometry', {}).get('location', {}).get('lat', None)
            location.lng = result.get('geometry', {}).get('location', {}).get('lng', None)
            location.place_id = result.get('place_id', {})
        location.creator = str(self.request.user)

        location.save()
        context = {
            "location": location
        }
        return render(request, self.template_name, context)

class LocationCreateView(CreateView):
    model = Location
    fields = ['name', 'zipcode', 'city', 'country', 'address']
    template_name = "locations/location_form.html"
    #permission_required = 'location.add_location'

class LocationUpdateView(UpdateView):
    model = Location
    # Not recommended (potential security issue if more fields added)
    fields = ['name', 'zipcode', 'city', 'country', 'address']
    template_name = "locations/location_form.html"
    #permission_required = 'location.change_location'


class LocationDeleteView(DeleteView):
    model = Location
    success_url = reverse_lazy('locations')
    template_name = "locations/location_confirm_delete.html"
    #permission_required = 'location.delete_location'

    def form_valid(self, form):
        try:
            self.object.delete()
            return render(self.success_url)
        except Exception as e:
            return render(
                reverse("location-delete", kwargs={"pk": self.object.pk})
            )
        

class MapListView(ListView):
    model = Map
    template_name = "pages/maps.html"

    def get_queryset(self):
        return (
            Map.objects.filter(creator=self.request.user)
        )

class MapDetailView(DetailView):
    model = Map

    template_name = "maps/map_detail.html"
    apikey = getattr(settings, 'GOOGLE_API_KEY', None)
        
    def get(self, request, pk): 
        # Get the map and its locations
        map = Map.objects.get(pk=pk)
        map_locations = map.locations.all()

        map.creator = str(self.request.user)
        map.save()
        
        # Generate the starting point, waypoints and destination parrameters for API call
        origin = f'{map.starting_location.lat},{map.starting_location.lng}'
        dest = f'{map.dest_location.lat},{map.dest_location.lng}'
        way_points = []
        for location in map_locations:
            # check to make sure this isn't the starting or end point
            print("In for loop")
            if location != map.starting_location and location != map.dest_location:
                print("Location name: ", location.name)
                way_points.append(f'{location.lat},{location.lng}')

        print("origin: ", origin)
        print()
        print("way_points: ", way_points)
        print()
        print("dest: ", dest)


        locations = []        
        address_string = ""
        apikey = getattr(settings, 'GOOGLE_API_KEY', None)
        print("map_locations: ", map_locations)
        
      #  buildPath(self, request, pk)
        for location in map_locations:          
            data = {
                'lat': float(location.lat),
                'lng': float(location.lng),
                'name': location.name
            }
            locations.append(data)

        origin = json.dumps(origin)
        way_points = json.dumps(way_points)
        dest = json.dumps(dest)

        context = {
            "map": map,
            "origin": origin,
            "way_points": way_points,
            "dest": dest,
            'address': address_string,
            "key": MapDetailView.apikey
        }

        return render(request, self.template_name, context)
        

class MapCreateView(CreateView):
    model = Map
    #fields = ['name', 'starting_location', 'dest_location', 'locations']
    template_name = "maps/map_form.html"

    def get(self, request):
        context = {
            "loc_list": Location.objects.filter(creator=self.request.user),
        }
        return render(request, self.template_name, context)


class MapUpdateView(UpdateView):
    model = Map
    # Not recommended (potential security issue if more fields added)
    fields = ['name', 'creator', 'zoom_level', 'locations', 'date']
    template_name = "maps/map_form.html"
    
class MapDeleteView(DeleteView):
    model = Map
    success_url = reverse_lazy('maps')
    template_name = "maps/map_confirm_delete.html"
   # permission_required = 'map.delete_map'

    def form_valid(self):
        try:
            self.object.delete()
            return render(self.success_url)
        except Exception as e:
            return render(
                reverse("map-delete", kwargs={"pk": self.object.pk}))
    