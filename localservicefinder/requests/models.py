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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)

    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)

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

    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    rating = models.PositiveIntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"{self.service.name} request by {self.user.username} ({self.status})"