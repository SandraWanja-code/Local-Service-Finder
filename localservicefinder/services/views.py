from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Service, Provider

@login_required
def become_provider(request):
    services = Service.objects.all()
    provider = Provider.objects.filter(user=request.user).first()
    success = False

    if request.method == "POST":
        selected_services = request.POST.getlist("services")  # 👈 gets all selected
        phone = request.POST.get("phone")
        location = request.POST.get("location")

        if provider:
            provider.phone = phone
            provider.location = location
            provider.services.set(selected_services)  # 👈 updates multiple services
            provider.save()
        else:
            provider = Provider.objects.create(
                user=request.user,
                phone=phone,
                location=location
            )
            provider.services.set(selected_services)

        success = True

    return render(request, "services/become_provider.html", {
        "services": services,
        "provider": provider,
        "success": success
    })
    
    
@login_required
def edit_provider(request):
    provider = Provider.objects.filter(user=request.user).first()
    services = Service.objects.all()
    success = False

    if request.method == "POST":
        selected_ids = request.POST.getlist("services")  # multiple selected
        new_services = request.POST.get("new_services", "").split(",")  # comma-separated

        # Clean new services (strip spaces & ignore empty)
        new_services = [s.strip() for s in new_services if s.strip()]

        # Create new services in DB if they don't exist
        for s in new_services:
            service_obj, created = Service.objects.get_or_create(name=s)
            selected_ids.append(service_obj.id)  # add new service to selected list

        # Get Service objects for all selected IDs
        service_objs = Service.objects.filter(id__in=selected_ids)

        # Create or update provider
        provider, created = Provider.objects.update_or_create(
            user=request.user,
            defaults={
                "phone": request.POST.get("phone"),
                "location": request.POST.get("location")
            }
        )
        provider.services.set(service_objs)  # set multiple services
        success = True

    return render(request, "services/edit_provider.html", {
        "provider": provider,
        "services": services,
        "success": success
    })