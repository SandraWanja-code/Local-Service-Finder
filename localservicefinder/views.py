from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import client_required, staff_required
from accounts.models import AccessLog, ClientProfile, SessionLog, UserManagementLog
from payments.models import PaymentRecord
from requests.models import ServiceRequest
from services.models import Service, Provider


def home(request):
    services = Service.objects.filter(is_active=True).order_by("name")[:6]
    providers = Provider.objects.filter(approval_status="approved", is_available=True).select_related("user")[:6]

    return render(request, "home.html", {
        "services": services,
        "providers": providers
    })


def role_redirect(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.user.is_staff:
        return redirect("admin_dashboard")
    if hasattr(request.user, "provider"):
        return redirect("provider_dashboard")
    return redirect("client_dashboard")


@client_required
def client_dashboard(request):
    requests_qs = ServiceRequest.objects.filter(user=request.user, deleted=False).select_related("service", "provider")
    active_requests = requests_qs.exclude(status="completed").order_by("-requested_at")[:5]
    services = Service.objects.filter(is_active=True).order_by("name")[:8]
    recommended_providers = Provider.objects.filter(
        approval_status="approved",
        is_available=True,
    ).select_related("user").prefetch_related("services")[:4]

    return render(request, "dashboards/client_dashboard.html", {
        "active_requests": active_requests,
        "services": services,
        "recommended_providers": recommended_providers,
        "total_requests": requests_qs.count(),
        "pending_requests": requests_qs.filter(status="pending").count(),
        "completed_requests": requests_qs.filter(status="completed").count(),
    })


def _admin_counts():
    return {
        "total_users": User.objects.count(),
        "total_clients": ClientProfile.objects.count(),
        "total_providers": Provider.objects.count(),
        "total_requests": ServiceRequest.objects.filter(deleted=False).count(),
        "pending_requests": ServiceRequest.objects.filter(status="pending", deleted=False).count(),
        "completed_requests": ServiceRequest.objects.filter(status="completed", deleted=False).count(),
        "total_services": Service.objects.count(),
        "total_revenue": PaymentRecord.objects.aggregate(total=Sum("amount_paid"))["total"] or 0,
    }


@staff_required
def admin_dashboard(request):
    status_counts = ServiceRequest.objects.filter(deleted=False).values("status").annotate(total=Count("id"))
    provider_counts = Provider.objects.values("approval_status").annotate(total=Count("id"))
    recent_requests = ServiceRequest.objects.select_related("user", "service", "provider__user").order_by("-requested_at")[:8]

    return render(request, "admin_portal/dashboard.html", {
        **_admin_counts(),
        "status_counts": list(status_counts),
        "provider_counts": list(provider_counts),
        "recent_requests": recent_requests,
        "recent_logs": AccessLog.objects.select_related("user").order_by("-created_at")[:6],
    })


@staff_required
def admin_users(request):
    query = request.GET.get("q", "").strip()
    users = User.objects.select_related("client_profile", "provider").order_by("-date_joined")
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    return render(request, "admin_portal/users.html", {**_admin_counts(), "users": users[:100], "query": query})


@staff_required
def admin_providers(request):
    if request.method == "POST":
        provider = get_object_or_404(Provider, id=request.POST.get("provider_id"))
        action = request.POST.get("action")
        if action in ["approved", "rejected", "pending"]:
            provider.approval_status = action
            provider.save()
            UserManagementLog.objects.create(
                admin_user=request.user,
                target_user=provider.user,
                action=f"provider_{action}",
                notes=request.POST.get("notes", ""),
            )
            messages.success(request, f"Provider status updated to {provider.get_approval_status_display()}.")
        return redirect("admin_providers")

    status = request.GET.get("status", "")
    providers = Provider.objects.select_related("user").prefetch_related("services").order_by("-id")
    if status:
        providers = providers.filter(approval_status=status)
    return render(request, "admin_portal/providers.html", {**_admin_counts(), "providers": providers, "status": status})


@staff_required
def admin_services(request):
    if request.method == "POST":
        service_id = request.POST.get("service_id")
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if service_id:
            service = get_object_or_404(Service, id=service_id)
            service.name = name
            service.description = description
            service.is_active = is_active
            service.save()
            messages.success(request, "Service updated.")
        elif name:
            Service.objects.create(name=name.title(), description=description, is_active=is_active)
            messages.success(request, "Service added.")
        return redirect("admin_services")

    services = Service.objects.annotate(provider_count=Count("providers")).order_by("name")
    return render(request, "admin_portal/services.html", {**_admin_counts(), "services": services})


@staff_required
def admin_requests(request):
    status = request.GET.get("status", "")
    requests_qs = ServiceRequest.objects.filter(deleted=False).select_related("user", "service", "provider__user").order_by("-requested_at")
    if status:
        requests_qs = requests_qs.filter(status=status)
    return render(request, "admin_portal/requests.html", {**_admin_counts(), "requests": requests_qs[:150], "status": status})


@staff_required
def admin_reports(request):
    return render(request, "admin_portal/reports.html", {
        **_admin_counts(),
        "status_counts": ServiceRequest.objects.filter(deleted=False).values("status").annotate(total=Count("id")),
        "session_logs": SessionLog.objects.select_related("user").order_by("-created_at")[:20],
    })


@staff_required
def admin_settings(request):
    return render(request, "admin_portal/settings.html", {**_admin_counts()})
