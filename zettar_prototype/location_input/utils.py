import requests
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.shortcuts import render
# from .models import Substations
import logging

def find_nearest_substation(location, substation_type):
    return
    """
    Returns the nearest substation of a specified type.

    This function uses a geospatial query to filter substations by type,
    calculates the distance from the given location using PostGIS functions,
    and returns the closest matching substation. If no substation is found,
    a warning is logged and None is returned.

    Args:
        location (Point) - the geographical location to search nearby
        substation_type (str) - One of 'Primary', 'Secondary', or 'BSP'

    Returns:
        The Substations model instance of nearest substation matching the type if found, else None
    
    Raises:
        TypeError: If location is not a Point object.
        ValueError: If substation_type is not valid.
        Logs a warning if no substation is found.
    """
    if not isinstance(location, Point):
        raise TypeError("location must be a Point object.")

    if substation_type not in {'Primary', 'Secondary', 'BSP'}:
        raise ValueError(f"Invalid substation_type: {substation_type}")

    nearest_substation = Substations.objects.filter(
        type=substation_type
    ).annotate(
        distance=Distance('geolocation', location)
    ).order_by('distance').first()

    if nearest_substation is None:
        logging.warning(f"Unexpected error - no substation found for type '{substation_type}' near location {location}")
        return None

    return nearest_substation


def public_path_network_distance(geolocation1, geolocation2):
    return
    """
    Calculate the public path network distance between two geolocations.

    This function sends a request to the OSRM API to compute the driving 
    distance between two geographic points. It parses the JSON response 
    and extracts the distance in meters. If the request fails or no valid 
    route is found, it returns None and logs the appropriate message.


    Args:
        geolocation1 (Point)
        geolocation2 (Point)

    Returns:
        float or None: The driving distance in meters if a route is found, else None.
    
    Raises:
        Logs a warning or error if:
            - The network request fails.
            - The response is invalid or missing expected fields.
    """

    lon1, lat1 = geolocation1.x, geolocation1.y
    lon2, lat2 = geolocation2.x, geolocation2.y
    url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{lon1},{lat1};{lon2},{lat2}?overview=false"
    )  

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if (
            isinstance(data, dict)
            and "routes" in data
            and isinstance(data["routes"], list)
            and len(data["routes"]) > 0
            and "distance" in data["routes"][0]
        ):
            return data["routes"][0]["distance"]
        else:
            logger.error("Error from OSRM: %s", data.get("message", "Unknown error"))
            return None

    except Exception as e:
        logger.error("Error decoding JSON response: %s", e)
        return None


def length_to_cost(length, substation_type):
    return
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