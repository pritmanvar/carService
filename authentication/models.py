from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=150, unique=True)
    phone_number = models.PositiveBigIntegerField(null=True, blank=True)
    user_type = models.CharField(default="normal", max_length=30)
    is_google_login = models.BooleanField(default=False)
    # To create custom user
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=[]


    objects = CustomUserManager()  # type: ignore[assignment]

    def __str__(self):
        return self.email


    