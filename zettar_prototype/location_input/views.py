from django.shortcuts import render

def location_form(request):
    return render(request, 'location_input/form.html')

def process_location(request):
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    
    # Just showing the values for now
    return render(request, 'location_input/confirmation.html', {
        'latitude': latitude,
        'longitude': longitude
    })