from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import ClientProfile, SessionLog
from .decorators import client_required


def _role_home(user):
    if user.is_staff:
        return "admin_dashboard"
    if hasattr(user, "provider"):
        return "provider_dashboard"
    return "client_dashboard"


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _remove_other_sessions(user, current_session_key):
    for session in Session.objects.filter(expire_date__gte=timezone.now()):
        data = session.get_decoded()
        if str(user.id) == str(data.get("_auth_user_id")) and session.session_key != current_session_key:
            session.delete()


def register(request):

    if request.method == "POST":

        username = request.POST["username"]
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        password = request.POST["password"]

        # check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        if email and User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("register")

        if ClientProfile.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already exists")
            return redirect("register")

        # create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        ClientProfile.objects.create(user=user, phone=phone)

        # automatically log them in
        login(request, user)
        _remove_other_sessions(user, request.session.session_key)
        SessionLog.objects.create(
            user=user,
            action="login",
            session_key=request.session.session_key or "",
            ip_address=_client_ip(request),
        )
        messages.success(request, "Account created successfully. Confirmation message sent to your email address.")

        return redirect("client_dashboard")

    return render(request, "register.html")


def login_view(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        login_identifier = username

        if "@" in login_identifier:
            matched_user = User.objects.filter(email__iexact=login_identifier).first()
            if matched_user:
                login_identifier = matched_user.username

        user = authenticate(request, username=login_identifier, password=password)

        if user is not None:
            if hasattr(user, "provider") and user.provider.approval_status == "rejected":
                messages.error(request, "Your provider account has been rejected. Contact the administrator.")
                return redirect("login")

            login(request, user)
            _remove_other_sessions(user, request.session.session_key)
            SessionLog.objects.create(
                user=user,
                action="login",
                session_key=request.session.session_key or "",
                ip_address=_client_ip(request),
            )
            return redirect(_role_home(user))
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


def logout_view(request):
    if request.user.is_authenticated:
        SessionLog.objects.create(
            user=request.user,
            action="logout",
            session_key=request.session.session_key or "",
            ip_address=_client_ip(request),
        )
    logout(request)
    return redirect("home")


@client_required
def profile(request):
    profile_obj, _created = ClientProfile.objects.get_or_create(
        user=request.user,
        defaults={"phone": ""},
    )

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()

        if email and User.objects.exclude(id=request.user.id).filter(email__iexact=email).exists():
            messages.error(request, "Email already exists")
            return redirect("profile")

        if phone and ClientProfile.objects.exclude(id=profile_obj.id).filter(phone=phone).exists():
            messages.error(request, "Phone number already exists")
            return redirect("profile")

        request.user.first_name = request.POST.get("first_name", "").strip()
        request.user.last_name = request.POST.get("last_name", "").strip()
        request.user.email = email
        request.user.save()

        profile_obj.phone = phone
        profile_obj.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    return render(request, "accounts/profile.html", {"profile": profile_obj})



@login_required
def delete_account(request):
    if request.method != "POST":
        return redirect("home")

    user = request.user
    logout(request)
    user.delete()

    messages.success(request, "Your account has been deleted.")
    return redirect("home")
