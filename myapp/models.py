from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Add any additional fields here
    # For example, is_admin and is_staff to distinguish between user types
    is_admin = models.BooleanField(default=False)
    is_staff_member = models.BooleanField(default=False)

class AdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # Add admin-specific fields here
    department = models.CharField(max_length=100)

class StaffProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # Add staff-specific fields here
    staff_id = models.CharField(max_length=100)

