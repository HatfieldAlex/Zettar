# pages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.about_view, name='about'),
    path('methodology/', views.methodology_view, name='methodology'),
    path('data/', views.data_view, name='data'),
]
