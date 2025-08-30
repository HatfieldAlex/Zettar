from collections import defaultdict
import logging

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.shortcuts import render

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
