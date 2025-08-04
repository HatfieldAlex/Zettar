from django.shortcuts import render
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
import json
import logging
from .models.substations import GSPSubstation, BSPSubstation, PrimarySubstation
from .models.new_connections import NewConnection
from collections import defaultdict
from .utils.view_helpers import find_nearest_substation_obj

@csrf_exempt
def get_estimate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            connection_type = data['connection_type']
            geolocation = Point(data['location']['lat'], data['location']['lng'], srid=4326)
            print(f'geolocation: {geolocation}')

            nearest_substation_obj = find_nearest_substation_obj(geolocation, connection_type)

            print(f'nearest_substation_obj: {nearest_substation_obj}')

            new_connection_objs = nearest_substation_obj.new_connections.all()

            print(f'new_connection_objs: {new_connection_objs}')

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

            print(f'connection_user_info: {connection_user_info}')
            
            
            connection_summary = {
                'nearest_substation_name': nearest_substation_obj.name,
                **dict(connection_user_info)  # Spread all metrics into top-level keys
            }

            print(f'connection_summary: {connection_summary}')
            

            return JsonResponse(connection_summary)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)


def home(request):
    return render(request, 'location_input/home.html')