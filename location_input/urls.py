from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('get_nearby_application_data/', views.get_nearby_application_data, name='get_nearby_application_data'),
]

