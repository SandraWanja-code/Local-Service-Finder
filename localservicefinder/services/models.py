from django.db import models
from django.contrib.auth.models import User

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Provider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service, blank=True)
    location = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    profile_image = models.ImageField(upload_to='provider_images/', null=True, blank=True)

    def __str__(self):
        return self.user.username


