from django.urls import path

from . import views
from .utils import get_nearby_substation_data

urlpatterns = [
    path("", views.home, name="home"),
    path("get_nearby_substation_data/", get_nearby_substation_data, name="get_nearby_substation_data"),
]
