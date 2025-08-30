import json

from django.conf import settings
from django.contrib.gis.geos import Point
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Substation
from .utils import find_nearest_substation_obj

@ensure_csrf_cookie
def get_nearby_application_data(request):
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
            connection_type = data["connection_type"]
            geolocation = Point(
                data["location"]["lat"], data["location"]["lng"], srid=4326
            )
            nearest_substation_obj = find_nearest_substation_obj(
                geolocation, connection_type
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


def home(request):
    """Render the home page with a location input form.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered homepage response.
    """
    return render(request, "location_input/home.html", {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    })
