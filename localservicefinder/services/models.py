from django.db import models
from django.contrib.auth.models import User

# -------------------------------
# SERVICE MODEL
# -------------------------------
class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# -------------------------------
# PROVIDER MODEL
# -------------------------------
class Provider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service, blank=True, related_name='providers')
    location = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    profile_image = models.ImageField(
        upload_to='provider_images/',
        default='provider_images/default.png',
        blank=True
    )

    def __str__(self):
        return self.user.username

# -------------------------------
# SERVICE REQUEST MODEL
# -------------------------------
class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
    ]

    PAYMENT_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_requests')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True, related_name='service_requests')

    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='unpaid')
    rating = models.PositiveIntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service.name} request by {self.user.username} ({self.status})"

# -------------------------------
# ADD is_provider PROPERTY TO USER
# -------------------------------
@property
def is_provider(self):
    return hasattr(self, 'provider')

User.add_to_class('is_provider', is_provider)