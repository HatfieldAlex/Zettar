from django.shortcuts import render
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import Substations 
from .utils import find_nearest_substation, get_osrm_driving_distance, length_to_cost
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
import json

@csrf_exempt
def get_estimate(request):
    data = json.loads(request.body)
    
    connection_type = data.get('connection_type')
    location = data.get('location')
    print(f'location: {location}')
    nearest_substation = find_nearest_substation(location['lat'], location['lng'], connection_type)
    print('---------------get here?')
    connection_length = get_osrm_driving_distance((location['lat'], location['lng']), nearest_substation.geolocation)
    cost_estimate = length_to_cost(connection_length, connection_type)

    return JsonResponse({'cost_estimate': cost_estimate})

def home(request):
    return render(request, 'location_input/home.html')