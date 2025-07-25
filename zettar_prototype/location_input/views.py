from django.shortcuts import render
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import Substations 
from .utils import get_osrm_driving_distance
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

def map_view(request):
    return render(request, 'map.html')

@csrf_exempt
def save_location(request):
    if request.method == 'POST':
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')
        print(f"Latitude: {lat}, Longitude: {lng}")
        # Optionally save to a model here
        return HttpResponse("Location saved successfully!")
    return HttpResponse("Invalid request", status=400)


def location_form(request):
    return render(request, 'location_input/form.html')

def map_visualisation(request):
    return render(request, 'location_input/map_visualisation.html')

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