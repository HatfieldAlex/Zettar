from django.shortcuts import render
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import Substations 
from .utils import get_osrm_driving_distance, length_to_cost
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse

import json

def map_view(request):
    return render(request, 'map.html')

@csrf_exempt
def get_estimate(request):
    data = json.loads(request.body)
    print(f'request data: {request}')
    connection_type = data.get('connection_type')
    location = data.get('location')
    print(f"Connection Type: {connection_type}")
    print(f"Location: {location}")
    cost_estimate = 5000
    print(f'cost_estimate: {cost_estimate}')
    print('----------------------------------------------')
    return JsonResponse({'cost_estimate': cost_estimate})

    # if request.method == 'POST':
    #     data = json.loads(request.body)
    #     connection_type = data.get('connection_type')
    #     location = data.get('location')
        
    #     print(f'location: {location}')

    #     estimate_text = {
    #         'primary': "Estimated Cost: £75,000 – £150,000",
    #         'secondary': "Estimated Cost: £50,000 – £100,000",
    #         'bsp': "Estimated Cost: £500,000+",
    #     }.get(connection_type, "Unknown connection type.")

    #     return JsonResponse({'estimate': estimate_text})

    # return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def save_location(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')

    try:
        lat = float(latitude)
        lon = float(longitude)
        user_location = Point(lon, lat, srid=4326)
    except (TypeError, ValueError):
        return render(request, 'location_input/confirmation.html', {
            'error': 'Invalid coordinates.',
        })

    # Find nearest substation
    nearest_substation = Substations.objects.annotate(
        distance=Distance('geolocation', user_location)
    ).order_by('distance').first()

    osrm_distance = None
    if nearest_substation and nearest_substation.geolocation:
        sub_lon = nearest_substation.geolocation.x
        sub_lat = nearest_substation.geolocation.y
        osrm_distance = get_osrm_driving_distance(
            (lon, lat), (sub_lon, sub_lat)
        )
        cost = length_to_cost(osrm_distance)

    return render(request, 'location_input/location_received.html', {
        'latitude': latitude,
        'longitude': longitude,
        'nearest_name': nearest_substation.name if nearest_substation else None,
        'nearest_location': nearest_substation.geolocation if nearest_substation else None,
        'osrm_distance': osrm_distance,
        'cost': cost
    })


def location_form(request):
    return render(request, 'location_input/form.html')

def home(request):
    return render(request, 'location_input/home.html')

def process_location(request):
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')

    try:
        lat = float(latitude)
        lon = float(longitude)
        user_location = Point(lon, lat, srid=4326)
    except (TypeError, ValueError):
        return render(request, 'location_input/confirmation.html', {
            'error': 'Invalid coordinates.',
        })

    # Find nearest substation
    nearest_substation = Substations.objects.annotate(
        distance=Distance('geolocation', user_location)
    ).order_by('distance').first()

    osrm_distance = None
    if nearest_substation and nearest_substation.geolocation:
        sub_lon = nearest_substation.geolocation.x
        sub_lat = nearest_substation.geolocation.y
        osrm_distance = get_osrm_driving_distance(
            (lon, lat), (sub_lon, sub_lat)
        )

    return render(request, 'location_input/confirmation.html', {
        'latitude': latitude,
        'longitude': longitude,
        'nearest_name': nearest_substation.name if nearest_substation else None,
        'nearest_location': nearest_substation.geolocation if nearest_substation else None,
        'osrm_distance': osrm_distance,
    })