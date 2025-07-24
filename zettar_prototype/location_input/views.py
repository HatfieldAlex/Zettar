from django.shortcuts import render

def location_form(request):
    return render(request, 'location_input/form.html')
