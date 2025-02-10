import decimal
from lib2to3.fixes.fix_methodattrs import MAP
from tokenize import String
from ninja import NinjaAPI, Schema
from localsights.users.models import User
from localsights.maps.models import Map, Location
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from typing import List
from datetime import date


# something
api = NinjaAPI()

class UserOut(Schema):
    id: int
    name: str
    first_name: str
    last_name: str
    username: str
    email: str

class LocationIn(Schema):
    name: str
    address: str
    city: str
    state: str
    country: str
    zipcode: int

class LocationOut(Schema):
    id: int
    name: str 
    address: str
    city: str
    # state: str
    country: str
    zipcode: str
    # latitude: float
    # longitude: float

class LocationId(Schema):
    id: int

class MapIn(Schema):
    name: str
    starting_location: int
    dest_location: int
    locations: List[int]

class MapOut(Schema):
    id: int
    name: str
    creator: str
    zoom_level: int
    starting_location: LocationId
    dest_location: LocationId
    locations: List[LocationId]

class MapId(Schema):
    id: int

class Coordinate(Schema):
    lat: float
    lng: float

class CoordinateRange(Schema): 
    point1: Coordinate
    point2: Coordinate

# Searching

# User Searches
@api.get("/search/users/username/{string}", response=List[UserOut])
def search_users_by_username(request, string: str):
    users = User.objects.filter(username__icontains=string).all().order_by('username')[:10:1]
    return users

@api.get("/search/users/first_name/{string}", response=List[UserOut])
def search_users_by_first_name(request, string: str):
    users = User.objects.filter(first_name__icontains=string).all().order_by('username')[:10:1]
    return users

@api.get("/search/users/last_name/{string}", response=List[UserOut])
def search_users_by_last_name(request, string: str):
    users = User.objects.filter(last_name__icontains=string).all().order_by('username')[:10:1]
    return users

@api.get("/search/users/email/{string}", response=List[UserOut])
def search_users_by_email(request, string: str):
    users = User.objects.filter(email__icontains=string).all().order_by('username')[:10:1]
    return users


# For when map and location models are implemnted

# # Map Searches
@api.get("/search/maps/name/{string}", response=List[MapId])
def search_maps_by_name(request, string: str):
    maps = Map.objects.filter(name__icontains=string).all().order_by('name')[:10:1]
    return maps

# @api.get("/search/maps/", response=List[MapOut])
# def search_maps_by_area(request, payload: LocationIn):
#     # some time of search bassed on location schema
#     return maps


# # Location searches
@api.get("/search/locations/name/{string}", response=List[LocationId])
def search_locations_by_name(request, string: str):
    location = Location.objects.filter(name__icontains=string).all().order_by('name')[:10:1]
    return location

@api.get("/search/locations/range", response=List[LocationId])
def search_locations_by_range(request, payload: CoordinateRange):
    # data = {**payload.dict()}
    # # print(data)
    location = Location.objects.filter(
        latitude__gt=payload.point1.lat, 
        latitude__lt=payload.point2.lat, 
        longitude__gt=payload.point1.lng, 
        longitude__lt=payload.point2.lng
    ).all()
    return location

# def search_locations_by_range(lat1, lat2, lng1, lng2) {
#     maps = Location.objects.filter(
#         lat__gt=lat1, 
#         lat__lt=lat2, 
#         lng__gt=lng1, 
#         lng__lt=lng2
#     ).all()[:10:1]
#     return map
# }

# @api.get("/search/locations/", response=List[MapOut])
# def search_locations_by_location(request, payload: LocationIn):
#     # some time of search bassed on location schema
#     return locations


# Getting

# get user by id
@api.get("/user/{id}", response=UserOut)
def get_user(request, id ):
    user = get_object_or_404(User, id = id)
    return user

# # gets map by id
# @api.get("/map/{id}", response=MapOut)
# def get_map(request, id ):
#     map = get_object_or_404(Map, id = id)
#     return map

# # gets location by id
@api.get("/location/{id}", response=LocationOut)
def get_location(request, id ):
    location = get_object_or_404(Location, id = id)
    return location


# Creating

# # Create new map
@api.post("/map", response=MapOut)
def create_map(request, payload: MapIn):
    print(request.user)
    print("====================================")
    map = Map.objects.create(
        name = payload.name,
        zoom_level = 1,
        starting_location = get_object_or_404(Location, id = payload.starting_location),
        dest_location = get_object_or_404(Location, id = payload.dest_location),
        date = date.today(),
        creator = str(request.user)
    )
    for i in payload.locations:
        map.locations.add(i)

    return map

# @api.post("/location")
# def create_location(request, payload: LocationIn):
#     Location.objects.create(**payload.dict());
#     return {"id": map.id}


# Editing

# @api.put("/map/{id}")
# def update_map(request, id: int, payload: MapIn):
#     map = get_object_or_404(request.User.maps, id=id)
#     for attr, value in payload.dict().items():
#         setattr(map, attr, value)
#     map.save()
#     return {"success": True}

# @api.put("/location/{id}")
# def update_location(request, id: int, payload: MapIn):
#     location = get_object_or_404(Location, id=id)
#     for attr, value in payload.dict().items():
#         setattr(location, attr, value)
#     location.save()
#     return {"success": True}

# Removing

# removes map from user 
# @api.delete("/map/{id}")
# def delete_map(request, id: int):
#     user = get_object_or_404(request.User.Maps, id=id)
#     user.delete()
#     return {"success": True}