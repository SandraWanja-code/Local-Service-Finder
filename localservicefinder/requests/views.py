from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from services.models import Service, Provider
from .models import ServiceRequest

@login_required
def request_service(request):

    services = Service.objects.all()

    if request.method == "POST":

        service_name = request.POST.get("service_name")
        description = request.POST.get("description")
        location = request.POST.get("location")

        service, created = Service.objects.get_or_create(name=service_name)

        service_request, created = ServiceRequest.objects.update_or_create(
            user=request.user,
            service=service,
            defaults={
                "description": description,
                "location": location
            }
        )

        providers = Provider.objects.filter(service=service)

        return render(request, "requests/matched_providers.html", {
            "providers": providers
        })

    return render(request, "requests/request_service.html", {
        "services": services
    })