

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from services.models import Service

class ServiceRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    description = models.TextField()
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, default="pending")

    def __str__(self):
        return f"{self.service} request by {self.user}"