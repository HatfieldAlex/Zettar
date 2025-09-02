from collections import defaultdict
import logging
import json

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Substation

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
        Substation
        .objects
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


@ensure_csrf_cookie
def get_nearby_substation_data(request):
    """
    Handle POST requests to estimate connection application insights near a location.

    Parses the JSON body of the request to extract connection type and geolocation,
    finds the nearest substation, aggregates connection counts and capacities from new connections,
    and returns a summary JSON response with the aggregated data.

    Args:
        request (HttpRequest): Django HTTP request object. Expects a JSON payload with:
            - connection_type (str): Type of the connection.
            - location (dict): Dictionary with latitude and longitude coordinates, 
            containing:
                - lat (float): Latitude.
                - lng (float): Longitude.

    Returns:
        JsonResponse: JSON containing the nearest substation name and aggregated application data,
                    or an error message with an appropriate HTTP status if the request is invalid.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            substation_type = data["substation_type"]
            geolocation = Point(
                data["location"]["lat"], data["location"]["lng"], srid=4326
            )
            nearest_substation_obj = find_nearest_substation_obj(
                geolocation, substation_type
            )
            substation_summary = {
                "nearest_substation_name": nearest_substation_obj.name,
                "nearest_substation_type": nearest_substation_obj.type,
            }
            return JsonResponse(substation_summary)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
    else:
        return JsonResponse(
            {"status": "error", "message": "Only POST method allowed"},
            status=405,
        )