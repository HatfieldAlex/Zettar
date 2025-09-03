from django.shortcuts import render
from django.views.generic import TemplateView


def about_view(request):
    return render(request, "pages/about.html")

