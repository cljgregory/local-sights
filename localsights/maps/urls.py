from django.urls import path
from .views import *


urlpatterns = [
    path("home", HomeView.as_view(), name='home'),
    path("maps", MapView.as_view(), name='maps'),
    path("geocoding/<int:pk>", GeocodingView.as_view(), name='geocoding'),
    path("distance", DistanceView.as_view(), name='distance'),
    path("display_map", DisplayMapView.as_view(), name='display_map'),
    
]
