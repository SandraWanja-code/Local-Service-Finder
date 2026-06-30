from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

# -------------------------------
# SERVICE MODEL
# -------------------------------
class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# -------------------------------
# PROVIDER MODEL
# -------------------------------
class Provider(models.Model):
    APPROVAL_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service, blank=True, related_name='providers')
    location = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    credentials = models.TextField(blank=True)
    portfolio = models.TextField(blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    availability = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='pending')
    profile_image = models.ImageField(
        upload_to='provider_images/',
        default='provider_images/default.png',
        blank=True
    )

    @property
    def average_rating(self):
        result = self.servicerequest_set.exclude(rating__isnull=True).aggregate(avg=Avg('rating'))
        return result['avg']

    def __str__(self):
        return self.user.username


class ApprovalRecord(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="approval_records")
    status = models.CharField(max_length=20, choices=Provider.APPROVAL_CHOICES)
    decided_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider.user.username} - {self.status}"


class ServiceCatalogueLog(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="catalogue_logs")
    action = models.CharField(max_length=100)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service.name} - {self.action}"


class SystemReport(models.Model):
    title = models.CharField(max_length=120)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_count = models.PositiveIntegerField(default=0)
    provider_count = models.PositiveIntegerField(default=0)
    booking_count = models.PositiveIntegerField(default=0)
    paid_transaction_count = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# -------------------------------
# SERVICE REQUEST MODEL
# -------------------------------
class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
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
