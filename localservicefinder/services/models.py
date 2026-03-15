
# Create your models here.
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
       return f"{self.user.username} - {', '.join([s.name for s in self.services.all()])}"