from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from .models import Service, Provider
from requests.models import ServiceRequest
from payments.models import PaymentRecord, TransactionLog
from accounts.models import AccessLog

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
        credentials = request.POST.get("credentials", "")
        portfolio = request.POST.get("portfolio", "")
        hourly_rate = request.POST.get("hourly_rate") or None
        availability = request.POST.get("availability", "")

        provider = Provider.objects.create(
            user=request.user,
            phone=phone,
            location=location,
            credentials=credentials,
            portfolio=portfolio,
            hourly_rate=hourly_rate,
            availability=availability,
        )

        if "profile_image" in request.FILES:
            provider.profile_image = request.FILES["profile_image"]
            provider.save()

        messages.success(request, "Provider profile submitted. An administrator must approve it before clients can book you.")
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
    all_services = Service.objects.filter(is_active=True)

    if request.method == "POST":
        if "update_profile" in request.POST:
            provider.phone = request.POST.get("phone", provider.phone)
            provider.location = request.POST.get("location", provider.location)
            provider.credentials = request.POST.get("credentials", provider.credentials)
            provider.portfolio = request.POST.get("portfolio", provider.portfolio)
            provider.availability = request.POST.get("availability", provider.availability)
            provider.hourly_rate = request.POST.get("hourly_rate") or None
            provider.is_available = request.POST.get("is_available") == "on"
            if "profile_image" in request.FILES:
                provider.profile_image = request.FILES["profile_image"]
            provider.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("my_services")

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

    if provider.approval_status != "approved":
        messages.warning(request, "Your provider profile is waiting for administrator approval.")
        return redirect("my_services")

    requests_qs = ServiceRequest.objects.filter(
        service__in=provider.services.all()
    ).filter(
        Q(status="pending") | Q(provider=provider)
    ).order_by("-requested_at")

    if request.method == "POST":
        req_id = request.POST.get("request_id")
        action = request.POST.get("action")

        req = get_object_or_404(
            ServiceRequest,
            id=req_id,
            service__in=provider.services.all()
        )

        if action == "accept":
            if req.status == "pending":
                req.status = "accepted"
                req.provider = provider
                messages.success(request, "Request accepted successfully.")

        elif action == "decline":
            if req.status == "pending":
                req.status = "declined"
                req.decline_reason = request.POST.get("decline_reason", "")
                messages.warning(request, "Request declined.")

        elif action == "complete":
            if req.status == "accepted" and req.provider == provider:
                req.status = "completed"
                messages.success(request, "Service marked as completed.")

        elif action == "record_payment":
            if req.status == "completed" and req.provider == provider:

                payment_method = request.POST.get("payment_method", "")
                amount_paid = request.POST.get("amount_paid") or 0
                mpesa_code = request.POST.get("mpesa_code", "")

                payment = PaymentRecord.objects.create(
                    service_request=req,
                    recorded_by=request.user,
                    payment_method=payment_method,
                    amount_paid=amount_paid,
                    mpesa_code=mpesa_code,
                )

                TransactionLog.objects.create(
                    payment_record=payment,
                    action="payment_recorded",
                    performed_by=request.user,
                )

                req.payment_status = "paid"
                messages.success(request, "Payment recorded successfully.")

        req.save()
        return redirect("provider_dashboard")

    earnings = PaymentRecord.objects.filter(
        service_request__provider=provider
    ).aggregate(total=Sum("amount_paid"))["total"] or 0

    return render(request, "services/provider_dashboard.html", {
        "requests": requests_qs,
        "earnings": earnings,
    })

# ===============================
# PROVIDERS BY SERVICE
# ===============================
def providers_by_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    location = request.GET.get("location", "").strip()
    providers = Provider.objects.filter(
        services=service,
        approval_status="approved",
        is_available=True,
    )
    if location:
        providers = providers.filter(location__icontains=location)

    return render(request, "services/providers_by_service.html", {
        "service": service,
        "providers": providers,
        "location": location,
    })


# ===============================
# PROVIDER PROFILE
# ===============================
def provider_profile(request, provider_id):
    provider = get_object_or_404(Provider, id=provider_id)
    if request.user.is_authenticated:
        AccessLog.objects.create(
            user=request.user,
            action="provider_profile_view",
            details=f"Viewed provider {provider.user.username}.",
        )

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

            review = request.POST.get("review", "")

            if rating:
                req.rating = int(rating)
                req.review = review
                req.save()
                messages.success(request, "Rating submitted.")
            else:
                messages.error(request, "Please select a rating.")

            return redirect("customer_requests")

        # -------- COMPLAINT --------
        complaint_id = request.POST.get("complaint_id")
        if complaint_id:
            req = get_object_or_404(ServiceRequest, id=complaint_id, user=request.user)
            complaint = request.POST.get("complaint", "").strip()

            if complaint:
                req.complaint = complaint
                req.complaint_status = "open"
                req.save()
                messages.success(request, "Complaint submitted for administrator review.")
            else:
                messages.error(request, "Please describe the complaint.")

            return redirect("customer_requests")

        # -------- DELETE REQUEST --------
        delete_id = request.POST.get("delete_id")
        if delete_id:
            req = get_object_or_404(ServiceRequest, id=delete_id, user=request.user)

            if req.status in ["pending", "declined"]:
                req.delete()
                messages.success(request, "Request deleted.")

            elif req.status == "completed" and req.payment_status == "paid":
                req.delete()
                messages.success(request, "Request deleted.")

            else:
                messages.error(request, "Cannot delete unless pending or completed & paid.")

            return redirect("customer_requests")

        # -------- FALLBACK --------
        messages.error(request, "Invalid request.")
        return redirect("customer_requests")

    return render(request, "services/customer_requests.html", {
        "requests": requests_qs
    })

# ===============================
# PROFILE (UPLOAD IMAGE)
# ===============================
@login_required
def profile(request):
    provider = request.user.provider

    if request.method == "POST":
        if 'profile_image' in request.FILES:
            provider.profile_image = request.FILES['profile_image']
            provider.save()
            messages.success(request, "Profile image updated successfully.")

    return render(request, 'profile.html', {
        'provider': provider
    })
    # views.py
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('home')
    return redirect('home')
