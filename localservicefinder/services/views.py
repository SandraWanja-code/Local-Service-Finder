from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Service, Provider
from requests.models import ServiceRequest


# REGISTER AS PROVIDER
@login_required
def become_provider(request):

    services = Service.objects.all()
    provider = Provider.objects.filter(user=request.user).first()
    success = False

    if request.method == "POST":

        selected_services = request.POST.getlist("services")
        phone = request.POST.get("phone")
        location = request.POST.get("location")

        if provider:
            provider.phone = phone
            provider.location = location
            provider.services.set(selected_services)
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


# EDIT PROVIDER INFO
@login_required
def edit_provider(request):

    provider = Provider.objects.filter(user=request.user).first()
    services = Service.objects.all()
    success = False

    if request.method == "POST":

        selected_ids = request.POST.getlist("services")
        new_services = request.POST.get("new_services", "").split(",")

        new_services = [s.strip() for s in new_services if s.strip()]

        for s in new_services:
            service_obj, created = Service.objects.get_or_create(name=s)
            selected_ids.append(service_obj.id)

        service_objs = Service.objects.filter(id__in=selected_ids)

        provider, created = Provider.objects.update_or_create(
            user=request.user,
            defaults={
                "phone": request.POST.get("phone"),
                "location": request.POST.get("location")
            }
        )

        provider.services.set(service_objs)

        success = True

    return render(request, "services/edit_provider.html", {
        "provider": provider,
        "services": services,
        "success": success
    })


# VIEW PROVIDERS BY SERVICE
def providers_by_service(request, service_id):

    service = get_object_or_404(Service, id=service_id)

    providers = Provider.objects.filter(services=service)

    return render(request, "services/providers_by_service.html", {
        "service": service,
        "providers": providers
    })


# PROVIDER PROFILE PAGE
def provider_profile(request, provider_id):

    provider = get_object_or_404(Provider, id=provider_id)

    return render(request, "services/provider_profile.html", {
        "provider": provider
    })


# PROVIDER DASHBOARD
@login_required
@login_required
def provider_dashboard(request):

    provider = Provider.objects.filter(user=request.user).first()

    # block customers from accessing dashboard
    if not provider:
        return redirect("home")

    requests = ServiceRequest.objects.filter(
        service__in=provider.services.all()
    ).order_by("-created_at")

    return render(request, "services/provider_dashboard.html", {
        "requests": requests
    })
    
def customer_requests(request):
      requests = ServiceRequest.objects.filter(user=request.user).order_by('_created_at')
      return render(request, "services/customer_requests.html", { "requests": requests

    })

def my_services(request):
    services = Service.objects.filter(provider__user=request.user)
    return render(request, 'services/my_services.html', {'services': services})



def delete_service(request, id):
    service = get_object_or_404(Service, id=id, provider__user=request.user)
    service.delete()
    return redirect('my_services')