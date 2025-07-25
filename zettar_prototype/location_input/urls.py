from django.urls import path
from . import views

urlpatterns = [
    path('', views.location_form, name='location_form'),
    path('process-location/', views.process_location, name='process_location'),
    path('map-visualisation/', views.map_visualisation, name='map_visualisation'),
    path('save-location/', views.save_location, name='save_location'),
]

