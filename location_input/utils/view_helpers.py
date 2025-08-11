from collections import defaultdict
import logging
from decimal import Decimal, ROUND_DOWN

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.shortcuts import render

from ..constants import APPLICATION_STATUS_FIELDS
from ..models.substations import Substation

def find_nearest_substation_obj(geolocation, substation_type):
    """
    Returns the nearest substation of a specified type.

    This function uses a geospatial query to filter substations by type,
    calculates the distance from the given location using PostGIS functions,
    and returns the closest matching substation. If no substation is found,
    a warning is logged and None is returned.

    Args:
        geolocation (Point) - the geographical location to search nearby
        substation_type (str) - One of 'primary', 'bsp', or 'gsp'

    Returns:
        The Substation model instance of nearest substation matching the type if found, else None

    Raises:
        TypeError: If geolocation is not a Point object.
        ValueError: If substation_type is not valid.
        Logs a warning if no substation is found.
    """
    if not isinstance(geolocation, Point):
        raise TypeError("geolocation must be a Point object.")

    if substation_type not in {"primary", "bsp", "gsp"}:
        raise ValueError(f"Invalid substation_type: {substation_type}")


    nearest_substation_obj = (
        Substation.objects
        .filter(type=substation_type)
        .annotate(distance=Distance("geolocation", geolocation))
        .order_by("distance")
        .first()
    )

    if nearest_substation_obj is None:
        logging.warning(
            f"Unexpected error - no substation found for type '{substation_type}' near geolocation {geolocation}"
        )
        return None

    return nearest_substation_obj


def get_substation_object_connection_data(substation_obj):
    """
    Aggregate connection data from new connections related to a substation.

    Iterates over all 'new_connections' associated with the given 'substation_obj' instance,
    summing demand and generation counts and capacities. Additionally aggregates counts
    by connection status fields defined in 'APPLICATION_STATUS_FIELDS'. Capacity values
    are rounded down to the nearest whole number.

    Args:
        substation_obj (ModelInstance): A substation model instance with a 'new_connections'
            related manager. Expected to have a 'name' attribute and type mappable via
            'substation_type_model_to_display_name'.

    Returns:
        dict: A summary dictionary containing:
            - nearest_substation_name (str): Name of the substation.
            - nearest_substation_type (str or None): Display name of the substation type.
            - demand_application_sum (int): Total demand application count.
            - demand_capacity_mw (Decimal): Total demand capacity in megawatts, rounded down.
            - generation_application_sum (int): Total generation application count.
            - generation_capacity_mw (Decimal): Total generation capacity in megawatts, rounded down.
            - demand_<status>_status_sum (int): Summed demand counts for each status in APPLICATION_STATUS_FIELDS.
            - generation_<status>_status_sum (int): Summed generation counts for each status in APPLICATION_STATUS_FIELDS.
    """
    connection_user_info = defaultdict(int)
    
    for obj in substation_obj.new_connections.all():

        demand_count = obj.demand_count or 0
        demand_capacity = obj.total_demand_capacity_mw or 0
        connection_user_info["demand_application_sum"] += demand_count
        connection_user_info["demand_capacity_mw"] += demand_capacity

        generation_count = obj.generation_count or 0
        generation_capacity = obj.total_generation_capacity_mw or 0
        connection_user_info["generation_application_sum"] += generation_count
        connection_user_info["generation_capacity_mw"] += generation_capacity

        connection_status = obj.connection_status.status
        if connection_status in APPLICATION_STATUS_FIELDS:
            connection_user_info[
                f"demand_{connection_status}_status_sum"
            ] += demand_count
            connection_user_info[
                f"generation_{connection_status}_status_sum"
            ] += generation_count

    if "demand_budget_status_sum" not in connection_user_info:
        connection_user_info["demand_budget_status_sum"] = 0 
    if "generation_budget_status_sum" not in connection_user_info:
        connection_user_info["generation_budget_status_sum"] = 0 
    if "demand_accepted_status_sum" not in connection_user_info:
        connection_user_info["demand_accepted_status_sum"] = 0
    if "generation_accepted_status_sum" not in connection_user_info:
        connection_user_info["generation_accepted_status_sum"] = 0
    if "demand_pending_status_sum" not in connection_user_info:
        connection_user_info["demand_pending_status_sum"] = 0
    if "generation_pending_status_sum" not in connection_user_info:
        connection_user_info["generation_pending_status_sum"] = 0

    demand_capacity_total = Decimal(
        connection_user_info["demand_capacity_mw"]
    ).quantize(Decimal("1"), rounding=ROUND_DOWN)
    generation_capacity_total = Decimal(
        connection_user_info["generation_capacity_mw"]
    ).quantize(Decimal("1"), rounding=ROUND_DOWN)

    connection_user_info["demand_capacity_mw"] = demand_capacity_total
    connection_user_info["generation_capacity_mw"] = generation_capacity_total

    connection_summary = {
        "nearest_substation_name": substation_obj.name,
        "nearest_substation_type": substation_obj.type,
        **dict(connection_user_info),
    }

    return connection_summary
