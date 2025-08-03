from django.shortcuts import render
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
# from .models import Substations 
from .utils import find_nearest_substation, public_path_network_distance, length_to_cost
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
import json
import logging
from .models.substations import GSPSubstation, BSPSubstation, PrimarySubstation
from .models.new_connections import NewConnection
from collections import defaultdict


@csrf_exempt
def get_estimate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            connection_type = data['connection_type']
            geolocation = Point(data['location']['lng'], data['location']['lat'], srid=4326)

            print(data)

            type_input_to_model = {
                'gsp': (GSPSubstation, 'gsp_substation'),
                'bsp': (BSPSubstation, 'bsp_substation'),
                'primary': (PrimarySubstation, 'primary_substation'),
            }
            substation_class, nc_field_name = type_input_to_model.get(connection_type)
            nearest_substation_obj = (
                substation_class.objects
                .filter(geolocation__isnull=False)
                .annotate(distance=Distance('geolocation', geolocation))
                .order_by('distance')
                .first()
            )

            filter_kwags = {nc_field_name: nearest_substation_obj}
            new_connection_objs = NewConnection.objects.filter(**filter_kwags)

            #variables to send back to front end
            #genera
            nearest_substation_name = nearest_substation_obj.name
            connection_user_info = defaultdict(int)
            status_fields = ['pending', 'budget', 'accepted']

            for obj in new_connection_objs:
                demand_count = obj.demand_count or 0
                demand_capacity = obj.total_demand_capacity_mw or 0
                generation_count = obj.generation_count or 0
                generation_capacity = obj.total_generation_capacity_mw or 0

                connection_user_info['demand_application_sum'] += demand_count
                connection_user_info['demand_capacity_mw'] += demand_capacity
                connection_user_info['generation_application_sum'] += generation_count
                connection_user_info['generation_capacity_mw'] += generation_capacity

                connection_status = obj.connection_status

                if connection_status in status_fields:
                    connection_user_info[f'demand_{connection_status}_status_sum'] += demand_count
                    connection_user_info[f'generation_{connection_status}_status_sum'] += generation_count

            # Final summary dictionary
            connection_summary = {
                'nearest_substation_name': nearest_substation_name,
                **dict(connection_user_info)  # Spread all metrics into top-level keys
            }

            print(connection_summary)
            

            return JsonResponse(connection_summary)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)
    # logger.error("logger eg")
    # data = json.loads(request.body)
    # connection_type = data.get('connection_type')
    # location = data.get('location')
    # nearest_substation = find_nearest_substation(location['lat'], location['lng'], connection_type)
    # connection_length = public_path_network_distance((location['lat'], location['lng']), nearest_substation.geolocation)
    # cost_estimate = length_to_cost(connection_length, connection_type)

    # return JsonResponse({'cost_estimate': cost_estimate})

def home(request):
    return render(request, 'location_input/home.html')