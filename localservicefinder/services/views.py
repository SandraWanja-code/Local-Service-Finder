from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Service, Provider
from requests.models import ServiceRequest



# ===============================
# BECOME PROVIDER
# ===============================
@login_required
def become_provider(request):
    provider = Provider.objects.filter(user=request.user).first()

    if provider:
        return redirect("my_services")

    if request.method == "POST":
        phone = request.POST.get("phone")
        location = request.POST.get("location")

        Provider.objects.create(
            user=request.user,
            phone=phone,
            location=location
        )
        return redirect("my_services")

    return render(request, "services/become_provider.html")


# ===============================
# MY SERVICES (CRUD)
# ===============================
@login_required
def my_services(request):
    provider = get_object_or_404(Provider, user=request.user)
    all_services = Service.objects.all()

    if request.method == "POST":
        service_id = request.POST.get("service_id")
        service_name = request.POST.get("service_name", "").strip().title()
        service_desc = request.POST.get("description", "")

        service = None

        # Select from dropdown
        if service_id:
            service = get_object_or_404(Service, id=service_id)

        # Manual entry
        elif service_name:
            service = Service.objects.filter(name__iexact=service_name).first()
            if not service:
                service = Service.objects.create(
                    name=service_name,
                    description=service_desc
                )

        # Add service
        if service and service not in provider.services.all():
            provider.services.add(service)

        # Delete service
        delete_id = request.POST.get("delete_id")
        if delete_id:
            service_to_delete = get_object_or_404(Service, id=delete_id)
            provider.services.remove(service_to_delete)

        return redirect("my_services")

    return render(request, "services/my_services.html", {
        "provider": provider,
        "all_services": all_services
    })


# ===============================
# PROVIDER DASHBOARD
# ===============================
@login_required
def provider_dashboard(request):
    provider = get_object_or_404(Provider, user=request.user)

    requests_qs = ServiceRequest.objects.filter(
        service__in=provider.services.all()
    ).order_by('-requested_at')

    if request.method == "POST":
        req_id = request.POST.get("request_id")
        action = request.POST.get("action")

        req = get_object_or_404(ServiceRequest, id=req_id)

        if action == "accept":
            req.status = "accepted"
            req.provider = provider 

        elif action == "decline":
            req.status = "declined"

        elif action == "complete":
            if req.status == "accepted":   # ✅ safety check
                req.status = "completed"

        req.save()
        return redirect("provider_dashboard")

    return render(request, "services/provider_dashboard.html", {
        "requests": requests_qs
    })


# ===============================
# CUSTOMER REQUESTS
# ===============================

@login_required
def customer_requests(request):
    requests_qs = ServiceRequest.objects.filter(
        user=request.user
    ).select_related("service").order_by("-requested_at")

    if request.method == "POST":
        req = get_object_or_404(ServiceRequest, id=request.POST.get("pay_id"), user=request.user)

        if req.status == "completed" and req.payment_status == "unpaid":
            req.payment_status = "paid"
            req.save()

        return redirect("customer_requests")

    return render(request, "services/customer_requests.html", {
        "requests": requests_qs
    })
    
    
# ===============================
# PROVIDERS BY SERVICE
# ===============================
def providers_by_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    providers = Provider.objects.filter(services=service)

    return render(request, "services/providers_by_service.html", {
        "service": service,
        "providers": providers
    })


# ===============================
# PROVIDER PROFILE
# ===============================
def provider_profile(request, provider_id):
    provider = get_object_or_404(Provider, id=provider_id)

    return render(request, "services/provider_profile.html", {
        "provider": provider
    })