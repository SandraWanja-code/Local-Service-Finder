from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone

from services.models import Service, Provider
from .models import ServiceRequest, SearchHistory, ProviderSelection
from accounts.models import AccessLog


# ===============================
# REQUEST A SERVICE
# ===============================
@login_required
def request_service(request):
    services = Service.objects.filter(is_active=True)
    providers = Provider.objects.filter(approval_status="approved", is_available=True)

    service_id = request.GET.get("service_id")
    selected_provider_id = request.GET.get("provider_id")
    location_query = request.GET.get("location", "").strip()

    if selected_provider_id:
        selected_provider = get_object_or_404(
            Provider,
            id=selected_provider_id,
            approval_status="approved",
            is_available=True,
        )
        providers = providers.filter(id=selected_provider.id)

        if not service_id and selected_provider.services.exists():
            service_id = str(selected_provider.services.first().id)

    if service_id:
        providers = providers.filter(services__id=service_id)

    if location_query:
        providers = providers.filter(location__icontains=location_query)

    if request.method == "GET" and (service_id or location_query):
        selected_service = Service.objects.filter(id=service_id).first() if service_id else None

        SearchHistory.objects.create(
            user=request.user,
            service=selected_service,
            location=location_query,
            results_count=providers.distinct().count(),
        )

    if request.method == "POST":
        service_id = request.POST.get("service_id")
        provider_id = request.POST.get("provider_id")
        location = request.POST.get("location", "")
        description = request.POST.get("description", "")
        requested_date = request.POST.get("requested_date") or None
        requested_time = request.POST.get("requested_time") or None

        if service_id:
            service = get_object_or_404(Service, id=service_id)
            provider = None

            if provider_id:
                provider = get_object_or_404(
                    Provider,
                    id=provider_id,
                    services=service,
                    approval_status="approved",
                    is_available=True,
                )

                ProviderSelection.objects.create(
                    user=request.user,
                    provider=provider,
                    service=service,
                )

            ServiceRequest.objects.create(
                user=request.user,
                service=service,
                provider=provider,
                location=location,
                description=description,
                requested_date=requested_date,
                requested_time=requested_time,
            )

            messages.success(request, "Your service request has been submitted!")
            return redirect("customer_requests")

        else:
            messages.error(request, "Please select a service before submitting.")

    return render(request, "requests/request_service.html", {
        "services": services,
        "providers": providers.distinct(),
        "selected_service_id": service_id,
        "selected_provider_id": selected_provider_id,
        "location_query": location_query,
    })


# ===============================
# CUSTOMER REQUESTS (VIEW + PAY STATUS ONLY)
# ===============================
@login_required
def customer_requests(request):
    requests_qs = ServiceRequest.objects.filter(user=request.user).order_by("-requested_at")

    AccessLog.objects.create(
        user=request.user,
        action="booking_history_view",
        details="Customer viewed booking history.",
    )

    if request.method == "POST":
        pay_id = request.POST.get("pay_id")
        req = get_object_or_404(ServiceRequest, id=pay_id, user=request.user)

        req.payment_status = "paid"
        req.save()

        return JsonResponse({"success": True})

    return render(request, "requests/customer_requests.html", {
        "requests": requests_qs
    })


# ===============================
# PROVIDER DASHBOARD
# ===============================
@login_required
def provider_dashboard(request):
    provider = get_object_or_404(Provider, user=request.user)

    requests_qs = ServiceRequest.objects.filter(
        service__in=provider.services.all()
    ).filter(
        Q(status="pending") | Q(provider=provider)
    ).order_by("-requested_at")

    if request.method == "POST":
        req = get_object_or_404(
            ServiceRequest,
            id=request.POST.get("request_id"),
            service__in=provider.services.all()
        )

        action = request.POST.get("action")

        if action == "accept":
            if req.status == "pending":
                req.status = "accepted"
                req.provider = provider

        elif action == "decline":
            if req.status == "pending":
                req.status = "declined"
                req.decline_reason = request.POST.get("decline_reason", "")

        elif action == "complete":
            if req.status == "accepted" and req.provider == provider:
                req.status = "completed"

        req.save()
        return redirect("provider_dashboard")


# ===============================
# DELETE REQUEST (SOFT DELETE)
# ===============================
@login_required
def delete_request(request, request_id):
    req = get_object_or_404(ServiceRequest, id=request_id, user=request.user)
    req.deleted = True
    req.save()

    messages.success(request, "Request deleted successfully!")
    return redirect("customer_requests")