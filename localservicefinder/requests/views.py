from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from services.models import Service, Provider
from .models import ServiceRequest


@login_required
def request_service(request):

    services = Service.objects.all()
    matching_providers = None
    success = False

    if request.method == "POST":

        service_name = request.POST.get("service_name")
        description = request.POST.get("description")
        location = request.POST.get("location")

        # find service or create if user typed new one
        service, created = Service.objects.get_or_create(name=service_name)

        # save request
        ServiceRequest.objects.create(
            user=request.user,
            service=service,
            location=location,
            description=description
        )

        # MATCHING STEP
        matching_providers = Provider.objects.filter(
            services=service
        )

        success = True

    return render(request, "requests/request_service.html", {
        "services": services,
        "success": success,
        "matching_providers": matching_providers
    })