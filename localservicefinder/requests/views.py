from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from services.models import Service, Provider
from .models import ServiceRequest
from django.contrib import messages

# ===============================
# REQUEST A SERVICE
# ===============================
@login_required
def request_service(request):
    services = Service.objects.all()  # available services

    if request.method == "POST":
        service_id = request.POST.get("service_id")
        location = request.POST.get("location", "")
        description = request.POST.get("description", "")

        if service_id:
            service = get_object_or_404(Service, id=service_id)

            # create request without assigning provider yet
            ServiceRequest.objects.create(
                user=request.user,
                service=service,
                location=location,
                description=description
            )
              # ✅ Add flash message
        messages.success(request, "Your service request has been submitted!")
    return redirect("customer_requests")

    return render(request, "requests/request_service.html", {"services": services})

# ===============================
# CUSTOMER REQUESTS (VIEW + PAY)
# ===============================
@login_required
def customer_requests(request):
    requests_qs = ServiceRequest.objects.filter(user=request.user).order_by("-requested_at")

    if request.method == "POST":
        pay_id = request.POST.get("pay_id")
        req = get_object_or_404(ServiceRequest, id=pay_id, user=request.user)
        req.payment_status = "paid"
        req.save()
        return JsonResponse({"success": True})

    return render(request, "requests/customer_requests.html", {"requests": requests_qs})

# ===============================
# PROVIDER DASHBOARD (VIEW + ACCEPT/DECLINE/COMPLETE)
# ===============================
@login_required
def provider_dashboard(request):
    provider = get_object_or_404(Provider, user=request.user)
    requests_qs = ServiceRequest.objects.filter(service__in=provider.services.all()).order_by("-requested_at")

    if request.method == "POST":
        req = get_object_or_404(ServiceRequest, id=request.POST.get("request_id"))
        action = request.POST.get("action")

        if action == "accept":
            req.status = "accepted"
            req.provider = provider  # assign current provider
        elif action == "decline":
            req.status = "declined"
        elif action == "complete":
            req.status = "completed"

        req.save()
        return redirect("provider_dashboard")

    return render(request, "requests/provider_dashboard.html", {"requests": requests_qs})