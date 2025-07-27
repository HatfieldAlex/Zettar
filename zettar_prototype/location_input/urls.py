from django.urls import path
from . import views

urlpatterns = [
    # path('', views.location_form, name='location_form'),
    # path('process-location/', views.process_location, name='process_location'),
    path('', views.home, name='home'),
    path('get-estimate/', views.get_estimate, name='get_estimate'),
]

