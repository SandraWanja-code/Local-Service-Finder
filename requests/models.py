from django.db import models
from django.contrib.auth.models import User
from services.models import Service, Provider


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

    COMPLAINT_STATUS_CHOICES = [
        ('none', 'No Complaint'),
        ('open', 'Open'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)

    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    requested_date = models.DateField(null=True, blank=True)
    requested_time = models.TimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='unpaid')

    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False)

    rating = models.PositiveIntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)

    decline_reason = models.TextField(blank=True)

    complaint = models.TextField(blank=True)
    complaint_status = models.CharField(
        max_length=20,
        choices=COMPLAINT_STATUS_CHOICES,
        default='none'
    )
    complaint_resolution = models.TextField(blank=True)

    def __str__(self):
        return f"{self.service.name} - {self.user.username}"


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="search_history")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    results_count = models.PositiveIntegerField(default=0)
    searched_at = models.DateTimeField(auto_now_add=True)


class ProviderSelection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="provider_selections")
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="selection_records")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    selected_at = models.DateTimeField(auto_now_add=True)
