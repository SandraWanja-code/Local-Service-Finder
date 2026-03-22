from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, Provider
from requests.models import ServiceRequest


# ===============================
# BECOME PROVIDER
# ===============================
@login_required
def become_provider(request):
    provider = Provider.objects.filter(user=request.user).first()

    if provider:
        messages.info(request, "You are already a provider.")
        return redirect("my_services")

    if request.method == "POST":
        phone = request.POST.get("phone")
        location = request.POST.get("location")

        Provider.objects.create(
            user=request.user,
            phone=phone,
            location=location
        )

        messages.success(request, "You are now a service provider!")
        return redirect("my_services")

    return render(request, "services/become_provider.html")


# ===============================
# MY SERVICES (PROVIDER ONLY)
# ===============================
@login_required
def my_services(request):
    if not hasattr(request.user, 'provider'):
        messages.error(request, "You must be a provider to access this page.")
        return redirect("home")

    provider = request.user.provider
    all_services = Service.objects.all()

    if request.method == "POST":
        service_id = request.POST.get("service_id")
        service_name = request.POST.get("service_name", "").strip().title()
        service_desc = request.POST.get("description", "")

        service = None

        if service_id:
            service = get_object_or_404(Service, id=service_id)

        elif service_name:
            service = Service.objects.filter(name__iexact=service_name).first()
            if not service:
                service = Service.objects.create(
                    name=service_name,
                    description=service_desc
                )

        if service and service not in provider.services.all():
            provider.services.add(service)
            messages.success(request, f"{service.name} added successfully.")

        # Remove service
        delete_id = request.POST.get("delete_id")
        if delete_id:
            service_to_delete = get_object_or_404(Service, id=delete_id)
            provider.services.remove(service_to_delete)
            messages.warning(request, "Service removed.")

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
            messages.success(request, "Request accepted successfully.")

        elif action == "decline":
            req.status = "declined"
            messages.warning(request, "Request declined.")

        elif action == "complete":
            if req.status == "accepted":
                req.status = "completed"
                messages.success(request, "Service marked as completed.")

        req.save()
        return redirect("provider_dashboard")

    return render(request, "services/provider_dashboard.html", {
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


# ===============================
# CUSTOMER REQUESTS
# ===============================
@login_required
def customer_requests(request):
    requests_qs = ServiceRequest.objects.filter(
        user=request.user
    ).select_related("service").order_by("-requested_at")

    if request.method == "POST":
        # -------- PAYMENT --------
        pay_id = request.POST.get("pay_id")
        if pay_id:
            req = get_object_or_404(ServiceRequest, id=pay_id, user=request.user)
            if req.status == "completed" and req.payment_status == "unpaid":
                req.payment_status = "paid"
                req.save()
                messages.success(request, "Payment successful via M-Pesa.")
            else:
                messages.warning(request, "Payment not allowed.")
            return redirect("customer_requests")

        # -------- RATING --------
        rate_id = request.POST.get("rate_id")
        if rate_id:
            req = get_object_or_404(ServiceRequest, id=rate_id, user=request.user)
            rating = request.POST.get("rating")
            if rating:
                req.rating = int(rating)
                req.save()
                messages.success(request, "Rating submitted.")
            else:
                messages.error(request, "Please select a rating.")
            return redirect("customer_requests")

        # -------- DELETE REQUEST --------
        delete_id = request.POST.get("delete_id")
        if delete_id:
            req = get_object_or_404(ServiceRequest, id=delete_id, user=request.user)
            if req.status == "pending":  # Only pending requests can be deleted
                req.delete()
                messages.success(request, "Request deleted successfully.")
            else:
                messages.error(request, "Cannot delete a request after provider accepted it.")
            return redirect("customer_requests")

        # Invalid action fallback
        messages.error(request, "Invalid request.")
        return redirect("customer_requests")

    return render(request, "services/customer_requests.html", {
        "requests": requests_qs
    })