import json

from django.conf import settings
from django.contrib.gis.geos import Point
from django.http import JsonResponse
from django.shortcuts import render


from .models import Substation
from .utils import find_nearest_substation_obj



def home(request):
    """Render the home page with a location input form.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered homepage response.
    """
    return render(request, "core/home.html", {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    })
