from django.urls import path
from . import views

urlpatterns = [
    path('', views.location_form, name='location_form'),
    path('process-location/', views.process_location, name='process_location'), 
]

