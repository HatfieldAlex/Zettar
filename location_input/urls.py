from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('get-estimate/', views.get_estimate, name='get_estimate'),
]

