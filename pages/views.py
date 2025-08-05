from django.shortcuts import render
from django.views.generic import TemplateView


def about_view(request):
    return render(request, "pages/about.html")


def methodology_view(request):
    return render(request, "pages/methodology.html")


def data_view(request):
    return render(request, "pages/data.html")
