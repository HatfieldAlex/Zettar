from django.http import HttpResponse

def location_form(request):
    return HttpResponse("<h1>Hello! This is the location input page.</h1>")

    # location = None
    # if request.method == 'POST':
    #     location = request.POST.get('location')

    # return render(request, 'location_input/form.html', {'location': location})
