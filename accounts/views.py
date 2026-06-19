from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import ClientProfile


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

        return redirect("home")

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
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("home")



@login_required
def delete_account(request):
    if request.method != "POST":
        return redirect("home")

    user = request.user
    logout(request)
    user.delete()

    messages.success(request, "Your account has been deleted.")
    return redirect("home")
