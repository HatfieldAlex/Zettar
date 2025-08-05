import json
import logging

from django.contrib.gis.db.models.functions import Distance
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.gis.geos import Point
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models.substations import GSPSubstation, BSPSubstation, PrimarySubstation
from .models.new_connections import NewConnection
from .utils.view_helpers import (
    find_nearest_substation_obj,
    get_substation_object_connection_data,
)


@ensure_csrf_cookie
def get_nearby_application_data(request):
    """
    Process POST requests to estimate connection statistics near a location.

    Parses request JSON body to extract connection type and location,
    finds the nearest substation, aggregates counts and capacities from new connections,
    and returns a summary JSON response of aggregated connection data.

    Args:
        request (HttpRequest): Django HTTP request object, expects JSON body with
                               'connection_type' and 'location' keys.

    Returns:
        JsonResponse: JSON containing nearest substation name and summed connection stats,
                      or error message with appropriate HTTP status for invalid requests.
    """

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            connection_type = data["connection_type"]
            geolocation = Point(
                data["location"]["lat"], data["location"]["lng"], srid=4326
            )
            nearest_substation_obj = find_nearest_substation_obj(
                geolocation, connection_type
            )
            connection_summary = get_substation_object_connection_data(
                nearest_substation_obj
            )
            print(f"connection_summary: {connection_summary}")
            return JsonResponse(connection_summary)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
    else:
        return JsonResponse(
            {"status": "error", "message": "Only POST method allowed"},
            status=405,
        )


def home(request):
    return render(request, "location_input/home.html")
