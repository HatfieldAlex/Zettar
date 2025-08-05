from collections import defaultdict
import logging
from decimal import Decimal, ROUND_DOWN

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.shortcuts import render

from ..models.substations import PrimarySubstation, BSPSubstation, GSPSubstation
from ..constants import APPLICATION_STATUS_FIELDS
from ..mappings import substation_type_abbr_to_model, substation_type_model_to_display_name


def find_nearest_substation_obj(geolocation, substation_type):
    """
    Returns the nearest substation of a specified type.

    This function uses a geospatial query to filter substations by type,
    calculates the distance from the given location using PostGIS functions,
    and returns the closest matching substation. If no substation is found,
    a warning is logged and None is returned.

    Args:
        geolocation (Point) - the geographical location to search nearby
        substation_type (str) - One of 'Primary', 'Secondary', or 'BSP'

    Returns:
        The Substations model instance of nearest substation matching the type if found, else None
    
    Raises:
        TypeError: If geolocation is not a Point object.
        ValueError: If substation_type is not valid.
        Logs a warning if no substation is found.
    """
    if not isinstance(geolocation, Point):
        raise TypeError("geolocation must be a Point object.")

    if substation_type not in {'primary', 'bsp', 'gsp'}:
        raise ValueError(f"Invalid substation_type: {substation_type}")

    substation_class = substation_type_abbr_to_model[f'{substation_type}']

    nearest_substation_obj = (
        substation_class.objects
        .annotate(distance=Distance('geolocation', geolocation))
        .order_by('distance')
        .first()
    )

    if nearest_substation_obj is None:
        logging.warning(f"Unexpected error - no substation found for type '{substation_type}' near geolocation {geolocation}")
        return None

    return nearest_substation_obj


def get_substation_object_connection_data(substation_obj):
    connection_user_info = defaultdict(int)

    # connection_status_freq = {
    #     'demand_pending': 0,
    #     'demand_budget': 0,
    #     'demand_accepted': 0,
    #     'generation_pending': 0,
    #     'generation_budget': 0,
    #     'generation_accepted': 0,
    # }
    
    for obj in substation_obj.new_connections.all():

        demand_count = obj.demand_count or 0
        demand_capacity = obj.total_demand_capacity_mw or 0
        connection_user_info['demand_application_sum'] += demand_count
        connection_user_info['demand_capacity_mw'] += demand_capacity
        # connection_status_freq[f'demand_{obj.status}'] += obj.demand_count

        generation_count = obj.generation_count or 0
        generation_capacity = obj.total_generation_capacity_mw or 0
        connection_user_info['generation_application_sum'] += generation_count
        connection_user_info['generation_capacity_mw'] += generation_capacity
        # connection_status_freq[f'generation_{obj.status}'] += obj.generation_count

        connection_status = obj.connection_status.status 
        if connection_status in APPLICATION_STATUS_FIELDS:
            connection_user_info[f'demand_{connection_status}_status_sum'] += demand_count
            connection_user_info[f'generation_{connection_status}_status_sum'] += generation_count

    # Convert summed capacities to Decimal and truncate decimals
    demand_capacity_total = Decimal(connection_user_info['demand_capacity_mw']).quantize(Decimal('1'), rounding=ROUND_DOWN)
    generation_capacity_total = Decimal(connection_user_info['generation_capacity_mw']).quantize(Decimal('1'), rounding=ROUND_DOWN)

    # Update the dict with truncated values
    connection_user_info['demand_capacity_mw'] = demand_capacity_total
    connection_user_info['generation_capacity_mw'] = generation_capacity_total
        
    connection_summary = {
            'nearest_substation_name': substation_obj.name,
            'nearest_substation_type': substation_type_model_to_display_name.get(type(substation_obj), None),
            **dict(connection_user_info)  
        }
            
    return connection_summary


