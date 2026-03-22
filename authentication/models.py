from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=150, unique=True)
    phone_number = models.PositiveBigIntegerField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    user_type = models.CharField(default="normal", max_length=30)
    is_google_login = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # To create custom user
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=[]


    objects = CustomUserManager()  # type: ignore[assignment]

    def __str__(self):
        return self.email


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Customer: {self.user.email}"

class Dealer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dealer_profile')
    company_name = models.CharField(max_length=255, null=True, blank=True)
    crm_webhook_url = models.URLField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dealer: {self.user.email}"