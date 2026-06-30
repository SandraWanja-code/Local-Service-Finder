from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def _is_provider(user):
    return hasattr(user, "provider")


def _is_approved_provider(user):
    return _is_provider(user) and user.provider.approval_status == "approved"


def client_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff or _is_provider(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def provider_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff or not _is_provider(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def approved_provider_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff or not _is_provider(request.user):
            raise PermissionDenied
        if not _is_approved_provider(request.user):
            messages.warning(request, "Your provider profile is waiting for administrator approval.")
            return redirect("my_services")
        return view_func(request, *args, **kwargs)

    return wrapper


def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper
