from django.shortcuts import render

def location_form(request):
    return render(request, 'location_input/form.html')

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import Substations  # adjust import if needed

def process_location(request):
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')

    # Convert to float and create a GEOS Point
    try:
        lat = float(latitude)
        lon = float(longitude)
        user_location = Point(lon, lat, srid=4326)
    except (TypeError, ValueError):
        return render(request, 'location_input/confirmation.html', {
            'error': 'Invalid coordinates.',
        })

    # Find the nearest substation
    nearest_substation = Substations.objects.annotate(
        distance=Distance('geolocation', user_location)
    ).order_by('distance').first()

    # Pass name and location to the template
    return render(request, 'location_input/confirmation.html', {
        'latitude': latitude,
        'longitude': longitude,
        'nearest_name': nearest_substation.name if nearest_substation else None,
        'nearest_location': nearest_substation.geolocation if nearest_substation else None,
    })

# def process_location(request):
#     latitude = request.POST.get('latitude')
#     longitude = request.POST.get('longitude')
    
#     # Just showing the values for now
#     return render(request, 'location_input/confirmation.html', {
#         'latitude': latitude,
#         'longitude': longitude
#     })