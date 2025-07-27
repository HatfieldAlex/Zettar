import requests
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.shortcuts import render
from .models import Substations


def find_nearest_substation(latitude, longitude, substation_type):
    try:
        lat = float(latitude)
        lon = float(longitude)
        user_location = Point(lon, lat, srid=4326)
    except (TypeError, ValueError):
        return render(request, 'location_input/confirmation.html', {
            'error': 'Invalid coordinates.',
        })

    # Find nearest substation of the specified type
    nearest_substation = Substations.objects.filter(
        type=substation_type
    ).annotate(
        distance=Distance('geolocation', user_location)
    ).order_by('distance').first()

    # Return None if no matching substation is found
    if nearest_substation is None:
        return None

    return nearest_substation


def get_osrm_driving_distance(coord1, coord2):

    lon1, lat1 = coord1
    lon2, lat2 = coord2

    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and data.get("code") == "Ok":
            # Distance is in meters
            return data["routes"][0]["distance"]
        else:
            print("Error from OSRM:", data.get("message", "Unknown error"))
            return None
    except Exception as e:
        print("Request failed:", e)
        return None


def length_to_cost(length, substation_type):
    if substation_type == 'Primary':
        # Upfront Cost: £19,263 is taken from Table 2.2, which lists the primary 33kV connection capitalised reinforcement cost.
        # Per metre cost: £112/m is from Table 3.1, which provides the unit cost of 33kV underground cables laid in public highway.
        return 19263 + 112*length
    elif substation_type == 'Secondary':
        # Upfront Cost: £5,501 corresponds to a secondary (LV) network connection, sourced from Table 2.2.
        # Per metre cost: £93/m is from Table 3.1, referring to LV cable laid underground in the public highway.
        return 5501 + 93*length
    elif substation_type == 'BSP':
        # Upfront Cost: £225,262 is the capitalised reinforcement cost of a 132kV BSP connection, from Table 2.2.
        # Per metre cost: £181/m from Table 3.1, based on 132kV cable installation in public highway.
        return 225262 + 181*length