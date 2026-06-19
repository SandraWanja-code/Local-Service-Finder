from django.db import models
from django.contrib.auth.models import User
from services.models import Service, Provider

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

    PAYMENT_METHOD_CHOICES = [
        ('', 'Not recorded'),
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
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

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='unpaid'
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, default='')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mpesa_code = models.CharField(max_length=30, blank=True)
    payment_recorded_at = models.DateTimeField(null=True, blank=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    rating = models.PositiveIntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    decline_reason = models.TextField(blank=True)
    complaint = models.TextField(blank=True)
    complaint_status = models.CharField(max_length=20, choices=COMPLAINT_STATUS_CHOICES, default='none')
    complaint_resolution = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['service', 'location']),
            models.Index(fields=['status', 'payment_status']),
        ]

    def __str__(self):
        return f"{self.service.name} request by {self.user.username} ({self.status})"


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="search_history")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    results_count = models.PositiveIntegerField(default=0)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} searched {self.service or 'all services'}"


class ProviderSelection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="provider_selections")
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="selection_records")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    selected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} selected {self.provider.user.username}"


class PaymentRecord(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="payment_records")
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=ServiceRequest.PAYMENT_METHOD_CHOICES)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_code = models.CharField(max_length=30, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service_request} - {self.amount_paid}"


class TransactionLog(models.Model):
    payment_record = models.ForeignKey(PaymentRecord, on_delete=models.CASCADE, related_name="transaction_logs")
    action = models.CharField(max_length=100)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - {self.payment_record}"
