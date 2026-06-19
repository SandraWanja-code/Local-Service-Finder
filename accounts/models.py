from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from services.models import Provider  # import your Provider model


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_profile")
    phone = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.user.username


class SessionLog(models.Model):
    ACTION_CHOICES = [
        ("login", "Login"),
        ("logout", "Logout"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="session_logs")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    session_key = models.CharField(max_length=80, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.action} at {self.created_at}"


class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="access_logs")
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"


class UserManagementLog(models.Model):
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="management_actions")
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="management_logs")
    action = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action}: {self.target_user.username}"


# ------------------------------
# Add helper properties to User
# ------------------------------

@property
def is_provider(self):
    # Returns True if the user has a Provider profile
    return hasattr(self, 'provider')

@property
def is_customer(self):
    # Returns True if the user does NOT have a Provider profile
    return not hasattr(self, 'provider')

# Add the properties to the default User model
User.add_to_class('is_provider', is_provider)
User.add_to_class('is_customer', is_customer)
