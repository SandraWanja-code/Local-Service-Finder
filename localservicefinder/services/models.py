# services/models.py

from django.db import models
from django.contrib.auth.models import User

class Service(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Provider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service)
    location = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)

    def __str__(self):
        # display provider username and offered services
        return f"{self.user.username} - {', '.join([s.name for s in self.services.all()])}"


class ServiceRequest(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="customer_requests"  # unique related_name
    )
    service = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE, 
        related_name="service_requests"  # unique related_name
    )
    location = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Status field
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.service.name} request by {self.user.username} ({self.status})"