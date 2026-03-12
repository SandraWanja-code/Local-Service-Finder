from django.shortcuts import render
from services.models import Service, Provider
from .models import ServiceRequest


def request_service(request):

    services = Service.objects.all()

    if request.method == "POST":

        service_id = request.POST["service"]
        description = request.POST["description"]
        location = request.POST["location"]

        service = Service.objects.get(id=service_id)

        service_request = ServiceRequest.objects.create(
            user=request.user,
            service=service,
            description=description,
            location=location
        )

        providers = Provider.objects.filter(service=service)

        return render(request, "requests/matched_providers.html", {
            "providers": providers
        })

    return render(request, "requests/request_service.html", {
        "services": services
    })