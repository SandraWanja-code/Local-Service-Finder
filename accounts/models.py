from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from services.models import Provider  # import your Provider model


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_profile")
    phone = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.user.username


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
