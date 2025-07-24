from django.shortcuts import render
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import Substations 
from .utils import get_osrm_driving_distance


def location_form(request):
    return render(request, 'location_input/form.html')

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