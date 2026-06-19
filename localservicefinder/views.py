from django.shortcuts import render
from services.models import Service, Provider

def home(request):

    services = Service.objects.all()[:6]  # show first 6
    providers = Provider.objects.all()[:6]

    return render(request, "home.html", {
        "services": services,
        "providers": providers
    })